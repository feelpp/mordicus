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



def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################

    collectionProblemData = SIO.LoadState("../MecaSequential/collectionProblemData")
    snapshotCorrelationOperator = SIO.LoadState("../MecaSequential/snapshotCorrelationOperator")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData("U")
    reducedOrderBases = collectionProblemData.GetReducedOrderBases()


    ##################################################
    # ONLINE
    ##################################################


    folder = "../../../../tests/TestsData/Zset/MecaSequentialOther/"
    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = PD.ProblemData("Online")
    onlineProblemData.SetDataFolder(folder)

    timeSequence = inputReader.ReadInputTimeSequence()

    constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
    onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)


    loadingList = inputReader.ConstructLoadingsList()
    onlineProblemData.AddLoading(loadingList)
    for loading in onlineProblemData.GetLoadingsForSolution("U"):
        loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBases, operatorCompressionData)


    initialCondition = inputReader.ConstructInitialCondition()
    onlineProblemData.SetInitialCondition(initialCondition)

    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator["U"])


    import time
    start = time.time()
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-8)
    print(">>>> DURATION ONLINE =", time.time() - start)
    onlineData = onlineProblemData.GetOnlineData("U")


    ## Compute Error
    numberOfNodes = mesh.GetNumberOfNodes()
    nbeOfComponentsPrimal = 3

    solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionUApprox.SetCompressedSnapshots(onlineCompressedSolution)
    solutionUApprox.UncompressSnapshots(reducedOrderBases["U"])

    solutionFileName = folder + "cube.ut"
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)
    solutionUExact = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
    for t in outputTimeSequence:
        U = solutionReader.ReadSnapshot("U", t, nbeOfComponentsPrimal, primality=True)
        solutionUExact.AddSnapshot(U, t)


    ROMErrors = []
    for t in outputTimeSequence:
        exactSolution = solutionUExact.GetSnapshotAtTime(t)
        approxSolution = solutionUApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrors.append(relError)

    print("ROMErrors =", ROMErrors)


    PW.WriteCompressedSolution(mesh, onlineCompressedSolution, reducedOrderBases["U"], "U")
    print("The compressed solution has been written in PXDMF Format")



    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

    dualNames = ["evrcum", "sig12", "sig23", "sig31", "sig11", "sig22", "sig33", "eto12", "eto23", "eto31", "eto11", "eto22", "eto33"]

    onlineProblemData.AddSolution(solutionUApprox)

    for name in dualNames:
        solutionsDual = S.Solution(name, 1, numberOfIntegrationPoints, primality = False)

        onlineDualCompressedSolution, gappyError = Meca.ReconstructDualQuantity(name, operatorCompressionData, onlineData, timeSequence = list(onlineCompressedSolution.keys()))

        solutionsDual.SetCompressedSnapshots(onlineDualCompressedSolution)

        onlineProblemData.AddSolution(solutionsDual)

    ZSW.WriteZsetSolution(mesh, meshFileName, "reduced", collectionProblemData, onlineProblemData, "U")



    folderHandler.SwitchToExecutionFolder()

    assert np.max(ROMErrors) < 0.01, "!!! Regression detected !!! ROMErrors have become too large"



if __name__ == "__main__":

    from BasicTools.Helpers import Profiler as P
    p = P.Profiler()
    p.Start()

    test()

    p.Stop()
    print(p)

