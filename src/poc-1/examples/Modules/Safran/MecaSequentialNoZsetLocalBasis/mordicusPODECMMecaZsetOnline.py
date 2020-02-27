from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical
from Mordicus.Core.IO import StateIO as SIO
import numpy as np
from pathlib import Path
import os
import time


def test():


    import time
    start = time.time()

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)



    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################

    collectionProblemDatas = [SIO.LoadState("mordicusState_Basis_0"), SIO.LoadState("mordicusState_Basis_1")]

    operatorCompressionDatas = [collectionProblemDatas[i].GetOperatorCompressionData() for i in range(2)]
    reducedOrderBasis = [collectionProblemDatas[i].GetReducedOrderBasis("U") for i in range(2)]

    snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")


    ##################################################
    # ONLINE
    ##################################################


    folder = "Computation1/"
    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = PD.ProblemData(folder)

    constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
    onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)

    loadingList = inputReader.ConstructLoadingsList()
    onlineProblemData.AddLoading(loadingList)

    initialCondition = inputReader.ConstructInitialCondition()
    initialCondition.ReduceInitialSnapshot(reducedOrderBasis[0], snapshotCorrelationOperator)

    onlineProblemData.SetInitialCondition(initialCondition)

    timeSequence = inputReader.ReadInputTimeSequence()
    timeSequences = [timeSequence[:len(timeSequence)//2], timeSequence[len(timeSequence)//2-1:]]


    onlinesolution = S.Solution("U", 1, mesh.GetNumberOfNodes(), primality = True)
    onlineProblemData.AddSolution(onlinesolution)

    initOnlineCompressedSnapshot = initialCondition.GetReducedInitialSnapshot()


    start = time.time()

    onlineCompressedSnapshots = []

    for i in range(2):

        for loading in loadingList:
            loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasis[i], operatorCompressionDatas[i])

        onlineCompressedSolution, onlineCompressionData = Mechanical.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequences[i], reducedOrderBasis[i], operatorCompressionDatas[i], 1.e-4)

        onlineCompressedSnapshots.append(onlineCompressedSolution)

        for t, compressedSnapshot in onlineCompressedSnapshots[i].items():
            onlinesolution.AddCompressedSnapshots(compressedSnapshot, t)

        if i==0:
            previousTime = timeSequences[i][-1]

            projectedReducedOrderBasis = collectionProblemDatas[0].GetDataCompressionData("projectedReducedOrderBasis_1")
            onlinesolution.ConvertCompressedSnapshotReducedOrderBasisAtTime(projectedReducedOrderBasis, previousTime)
            initOnlineCompressedSnapshot = onlinesolution.GetCompressedSnapshotsAtTime(previousTime)



    print("duration online =", time.time() - start)


    PW.WritePXDMF(mesh, onlineCompressedSnapshots[0], reducedOrderBasis[0], "U_reduced0")
    PW.WritePXDMF(mesh, onlineCompressedSnapshots[1], reducedOrderBasis[1], "U_reduced1")
    print("The compressed solution has been written in PXDMF Format")

    PW.WriteReducedOrderBasisToPXDMF(mesh, reducedOrderBasis[0], "U0")
    PW.WriteReducedOrderBasisToPXDMF(mesh, reducedOrderBasis[1], "U1")
    print("The reduced order basis has been written in PXDMF Format")


    #CHECK ACCURACY

    solutionFileName = folder + "cube.ut"
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)

    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    nbeOfComponentsPrimal = 3

    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
    solution = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    for time in outputTimeSequence:
        U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
        solution.AddSnapshot(U, time)


    print("check U")
    rel = [] 
    for t in onlinesolution.GetTimeSequenceFromCompressedSnapshots():
        if t < timeSequence[len(timeSequence)//2-1]:
            i = 0
        else:
            i = 1
        exact = solution.GetSnapshotAtTime(t)
        normExact = np.linalg.norm(exact)
        reconstructed = np.dot(reducedOrderBasis[i].T, onlineCompressedSnapshots[i][t])
        relError = np.linalg.norm(reconstructed - exact)
        if normExact > 0:
            relError /= normExact
        rel.append(relError)

    print("rel error =", rel)

    os.chdir(initFolder)

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
