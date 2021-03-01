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

    collectionProblemData = SIO.LoadState("collectionProblemData")

    snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBases = collectionProblemData.GetReducedOrderBases()


    ##################################################
    # ONLINE
    ##################################################


    folder = "MecaSequential/"
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

    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)


    import time
    start = time.time()
    onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-8)
    print(">>>> DURATION ONLINE =", time.time() - start)



    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

    dualNames = ["evrcum", "sig12", "sig23", "sig31", "sig11", "sig22", "sig33", "eto12", "eto23", "eto31", "eto11", "eto22", "eto33"]


    for name in dualNames:
        solutionsDual = S.Solution(name, 1, numberOfIntegrationPoints, primality = False)

        onlineDualCompressedSolution, errorGappy = Meca.ReconstructDualQuantity(name, operatorCompressionData, onlineCompressionData, timeSequence = list(onlineCompressedSolution.keys()))

        solutionsDual.SetCompressedSnapshots(onlineDualCompressedSolution)

        onlineProblemData.AddSolution(solutionsDual)

        print(name+" error Gappy ", errorGappy)



    onlineEvrcumCompressedSolution = onlineProblemData.GetSolution("evrcum").GetCompressedSnapshots()


    ## Compute Error

    nbeOfComponentsPrimal = 3
    numberOfNodes = mesh.GetNumberOfNodes()
    solutionFileName = folder + "cube.ut"
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
        if norml2ExactSolution > 1.e-2:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsEvrcum.append(relError)

        exactSolution = solutionUExact.GetSnapshotAtTime(t)
        approxSolution = solutionUApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution > 1.e-2:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsU.append(relError)

    print("ROMErrors U =", ROMErrorsU)
    print("ROMErrors Evrcum =", ROMErrorsEvrcum)

    PW.WritePXDMF(mesh, onlineCompressedSolution, reducedOrderBases["U"], "U")
    print("The compressed solution has been written in PXDMF Format")

    onlineProblemData.AddSolution(solutionUApprox)


    ZSW.WriteZsetSolution(mesh, meshFileName, "reduced", collectionProblemData, onlineProblemData, "U")


    folderHandler.SwitchToExecutionFolder()

    assert np.max(ROMErrorsU) < 1.e-4, "!!! Regression detected !!! ROMErrors have become too large"
    assert np.max(ROMErrorsEvrcum) < 5.e-2, "!!! Regression detected !!! ROMErrors have become too large"



if __name__ == "__main__":


    from BasicTools.Helpers import Profiler as P
    p = P.Profiler()
    p.Start()

    test()

    p.Stop()
    print(p)


