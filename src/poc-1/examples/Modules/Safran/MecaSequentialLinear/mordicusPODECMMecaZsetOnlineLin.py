from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import Solution as S
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
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")


    ##################################################
    # ONLINE
    ##################################################


    folder = "Computation1/"
    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = PD.ProblemData(folder)

    timeSequence = inputReader.ReadInputTimeSequence()

    constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
    onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)

    loadingList = inputReader.ConstructLoadingsList()
    for loading in loadingList:
        loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasisU, operatorCompressionData)
    onlineProblemData.AddLoading(loadingList)

    initialCondition = inputReader.ConstructInitialCondition()
    initialCondition.ReduceInitialSnapshot("U", reducedOrderBasisU, snapshotCorrelationOperator)

    onlineProblemData.SetInitialCondition(initialCondition)

    initOnlineCompressedSnapshot = initialCondition.GetReducedInitialSnapshot("U")


    import time
    start = time.time()
    onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-6)
    print(">>>> DURATION ONLINE =", time.time() - start)


    ## Compute Error
    numberOfNodes = mesh.GetNumberOfNodes()
    nbeOfComponentsPrimal = 3

    solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionUApprox.SetCompressedSnapshots(onlineCompressedSolution)
    solutionUApprox.UncompressSnapshots(reducedOrderBasisU)

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


    PW.WritePXDMF(mesh, onlineCompressedSolution, reducedOrderBasisU, "U")
    print("The compressed solution has been written in PXDMF Format")


    folderHandler.SwitchToExecutionFolder()

    assert np.max(ROMErrors) < 1.e-3, "!!! Regression detected !!! ROMErrors have become too large"


if __name__ == "__main__":
    test()


