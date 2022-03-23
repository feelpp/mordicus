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
    reducedOrderBases = collectionProblemData.GetReducedOrderBases()


    ##################################################
    # ONLINE
    ##################################################


    folder = "Computation1/"
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
    onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-6)
    print(">>>> DURATION ONLINE =", time.time() - start)


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


    folderHandler.SwitchToExecutionFolder()

    assert np.max(ROMErrors) < 1.e-3, "!!! Regression detected !!! ROMErrors have become too large"


if __name__ == "__main__":

    from BasicTools.Helpers import Profiler as P
    p = P.Profiler()
    p.Start()

    test()

    p.Stop()
    print(p)
