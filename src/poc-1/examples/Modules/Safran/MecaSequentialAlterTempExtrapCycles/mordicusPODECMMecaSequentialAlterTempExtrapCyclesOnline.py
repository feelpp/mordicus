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
from Mordicus.Core.Containers import Solution as S
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

    collectionProblemData = SIO.LoadState("collectionProblemData")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData("U")

    reducedOrderBases = collectionProblemData.GetReducedOrderBases()


    ##################################################
    # ONLINE
    ##################################################


    folder = "MecaAlternateTempDefinition/"
    inputFileName = folder + "cube2cycles.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)


    onlineProblemData = collectionProblemData.GetProblemData(config = "case-1")
    onlineProblemData.SetDataFolder(folder)


    timeSequence = inputReader.ReadInputTimeSequence()

    inputLoadingTemperature = inputReader.ConstructLoadingsList(loadingTags = ["temperature"])[0]
    assert inputLoadingTemperature.type == "temperature"


    onlineProblemDataTempLoading = onlineProblemData.GetLoadingsOfType("temperature")[0]
    onlineProblemDataTempLoading.UpdateLoading(inputLoadingTemperature)
    onlineProblemDataTempLoading.ReduceLoading()


    import time
    start = time.time()
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-8)
    print(">>>> DURATION ONLINE =", time.time() - start)
    onlineData = onlineProblemData.GetOnlineData("U")

    numberOfIntegrationPoints = onlineProblemData.GetSolution("evrcum").numberOfDOFs


    dualNames = ["evrcum", "sig12", "sig23", "sig31", "sig11", "sig22", "sig33", "eto12", "eto23", "eto31", "eto11", "eto22", "eto33"]


    for name in dualNames:
        solutionsDual = S.Solution(name, 1, numberOfIntegrationPoints, primality = False)

        onlineDualCompressedSolution, errorGappy = Meca.ReconstructDualQuantity(name, operatorCompressionData, onlineData, timeSequence = list(onlineCompressedSolution.keys()))

        solutionsDual.SetCompressedSnapshots(onlineDualCompressedSolution)

        onlineProblemData.AddSolution(solutionsDual)


    onlineEvrcumCompressedSolution = onlineProblemData.GetSolution("evrcum").GetCompressedSnapshots()


    ## Compute Error

    nbeOfComponentsPrimal = onlineProblemData.GetSolution("U").nbeOfComponents
    numberOfNodes = onlineProblemData.GetSolution("U").numberOfNodes


    solutionFileName = "MecaAlternateTempDefinition/cube.ut"
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)
    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

    solutionEvrcumExact  = S.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    solutionUExact = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    for t in outputTimeSequence:
        evrcum = solutionReader.ReadSnapshotComponent("evrcum", t, primality=False)
        solutionEvrcumExact.AddSnapshot(evrcum, t)
        U = solutionReader.ReadSnapshot("U", t, nbeOfComponentsPrimal, primality=True)
        solutionUExact.AddSnapshot(U, t)

    solutionEvrcumApprox = S.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    solutionEvrcumApprox.SetCompressedSnapshots(onlineEvrcumCompressedSolution)
    solutionEvrcumApprox.UncompressSnapshots(reducedOrderBases["evrcum"])

    solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionUApprox.SetCompressedSnapshots(onlineCompressedSolution)
    solutionUApprox.UncompressSnapshots(reducedOrderBases["U"])

    ROMErrorsU = []
    ROMErrorsEvrcum = []
    for t in outputTimeSequence:
        exactSolution = solutionEvrcumExact.GetSnapshotAtTime(t)
        approxSolution = solutionEvrcumApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution > 1.e-10:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsEvrcum.append(relError)

        exactSolution = solutionUExact.GetSnapshotAtTime(t)
        approxSolution = solutionUApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution > 1.e-10:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsU.append(relError)


    print("ROMErrors U =", ROMErrorsU)
    print("ROMErrors Evrcum =", ROMErrorsEvrcum)


    onlineProblemData.AddSolution(solutionUApprox)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)
    ZSW.WriteZsetSolution(mesh, meshFileName, "reduced", collectionProblemData, onlineProblemData, "U")


    folderHandler.SwitchToExecutionFolder()

    assert np.max(ROMErrorsU) < 1.e-4, "!!! Regression detected !!! ROMErrors have become too large"
    assert np.max(ROMErrorsEvrcum) < 1.e-3, "!!! Regression detected !!! ROMErrors have become too large"



if __name__ == "__main__":


    from BasicTools.Helpers import Profiler as P
    p = P.Profiler()
    p.Start()

    test()

    p.Stop()
    print(p)


