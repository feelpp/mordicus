# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Modules.Safran.IO import ZsetSolutionWriter as ZSW
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical as Meca
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Core.Helpers import FolderHandler as FH
import numpy as np
import os.path


def run():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()


    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################

    collectionProblemData = SIO.LoadState("collectionProblemData")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBases = collectionProblemData.GetReducedOrderBases()


    ##################################################
    # ONLINE
    ##################################################


    folder = "MecaSequentialSimpleMises/"
    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = PD.ProblemData("Online")
    onlineProblemData.SetDataFolder(folder)

    timeSequence = inputReader.ReadInputTimeSequence()


    from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MfrontConstitutiveLaw as MCL
    MfrontLaw = MCL.MfrontConstitutiveLaw("ALLELEMENT")
    MfrontLaw.SetDensity(1.e-8)
    internalVariables = ['eel11', 'eel22', 'eel33', 'eel12', 'eel23', 'eel31', 'epcum']
    nRedIntegPoints = len(operatorCompressionData['reducedIntegrationPoints'])

    if os.path.isfile(folder+'src/libBehaviour.so') == False:
        import subprocess
        os.chdir(folder)
        subprocess.call("./compileMfrontLaw.sh")
        folderHandler.SwitchToScriptFolder()

    MfrontLaw.SetLawModelling('Tridimensional', 'IsotropicLinearHardeningMises', folder+'src/libBehaviour.so', internalVariables, nRedIntegPoints)
    onlineProblemData.AddConstitutiveLaw([MfrontLaw])


    loadingList = inputReader.ConstructLoadingsList()
    onlineProblemData.AddLoading(loadingList)
    for loading in onlineProblemData.GetLoadingsForSolution("U"):
        loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBases, operatorCompressionData)
        #if loading.GetType() == 'centrifugal':
        #    loading.HyperReduceLoading(mesh, onlineProblemData, reducedOrderBases, operatorCompressionData)


    initialCondition = inputReader.ConstructInitialCondition()
    onlineProblemData.SetInitialCondition(initialCondition)

    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)


    import time
    start = time.time()
    onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-8)
    print(">>>> DURATION ONLINE =", time.time() - start)



    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

    dualNames = ["epcum", "sig12", "sig23", "sig31", "sig11", "sig22", "sig33", "eto12", "eto23", "eto31", "eto11", "eto22", "eto33"]


    for name in dualNames:
        solutionsDual = S.Solution(name, 1, numberOfIntegrationPoints, primality = False)

        onlineDualCompressedSolution, errorGappy = Meca.ReconstructDualQuantity(name, operatorCompressionData, onlineCompressionData, timeSequence = list(onlineCompressedSolution.keys()))

        solutionsDual.SetCompressedSnapshots(onlineDualCompressedSolution)

        onlineProblemData.AddSolution(solutionsDual)

        print(name+" error Gappy ", errorGappy)



    onlineepcumCompressedSolution = onlineProblemData.GetSolution("epcum").GetCompressedSnapshots()


    ## Compute Error

    nbeOfComponentsPrimal = 3
    numberOfNodes = mesh.GetNumberOfNodes()
    solutionFileName = folder + "cube.ut"
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)
    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

    solutionepcumExact  = S.Solution("epcum", 1, numberOfIntegrationPoints, primality = False)
    solutionUExact = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    for t in outputTimeSequence:
        epcum = solutionReader.ReadSnapshotComponent("epcum", t, primality=False)
        solutionepcumExact.AddSnapshot(epcum, t)
        U = solutionReader.ReadSnapshot("U", t, nbeOfComponentsPrimal, primality=True)
        solutionUExact.AddSnapshot(U, t)

    solutionepcumApprox = S.Solution("epcum", 1, numberOfIntegrationPoints, primality = False)
    solutionepcumApprox.SetCompressedSnapshots(onlineepcumCompressedSolution)
    solutionepcumApprox.UncompressSnapshots(reducedOrderBases["epcum"])

    solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionUApprox.SetCompressedSnapshots(onlineCompressedSolution)
    solutionUApprox.UncompressSnapshots(reducedOrderBases["U"])

    ROMErrorsU = []
    ROMErrorsepcum = []
    for t in outputTimeSequence:
        exactSolution = solutionepcumExact.GetSnapshotAtTime(t)
        approxSolution = solutionepcumApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution > 1.e-3:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsepcum.append(relError)

        exactSolution = solutionUExact.GetSnapshotAtTime(t)
        approxSolution = solutionUApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution > 1.e-3:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsU.append(relError)

    print("ROMErrors U =", ROMErrorsU)
    print("ROMErrors epcum =", ROMErrorsepcum)

    PW.WritePXDMF(mesh, onlineCompressedSolution, reducedOrderBases["U"], "U")
    print("The compressed solution has been written in PXDMF Format")

    onlineProblemData.AddSolution(solutionUApprox)


    ZSW.WriteZsetSolution(mesh, meshFileName, "reduced", collectionProblemData, onlineProblemData, "U")


    folderHandler.SwitchToExecutionFolder()

    assert np.max(ROMErrorsU) < 5.e-3, "!!! Regression detected !!! ROMErrors have become too large"
    assert np.max(ROMErrorsepcum) < 5.e-3, "!!! Regression detected !!! ROMErrors have become too large"



if __name__ == "__main__":


    from BasicTools.Helpers import Profiler as P
    p = P.Profiler()
    p.Start()

    run()

    p.Stop()
    print(p)


