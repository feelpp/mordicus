# -*- coding: utf-8 -*-
import numpy as np
import os
from Mordicus.Modules.Safran.OperatorCompressors import Thermal_transient as Th
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Core import GetTestDataPath
from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.FE import FETools as FT




def test():


    #################################################################
    ### OFFLINE
    #################################################################


    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    inputFileName = folder + "cube.inp"
    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"

    meshReader = ZMR.ZsetMeshReader(meshFileName)
    inputReader = ZIR.ZsetInputReader(inputFileName)
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)


    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")



    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    nbeOfComponentsPrimal = 1


    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()


    solutionT = Solution.Solution("T", nbeOfComponentsPrimal, numberOfNodes, primality = True)

    for time in outputTimeSequence:
        T = solutionReader.ReadSnapshot("TP", time, nbeOfComponentsPrimal, primality=True)
        solutionT.AddSnapshot(T, time)

    problemData = ProblemData.ProblemData(folder)
    problemData.AddSolution(solutionT)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)


    print("ComputeL2ScalarProducMatrix...")
    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 1)
    collectionProblemData.SetSnapshotCorrelationOperator("T", l2ScalarProducMatrix)

    reducedOrderBasisT = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "T", 1.e-3)
    collectionProblemData.AddReducedOrderBasis("T", reducedOrderBasisT)

    Th.CompressOperator(collectionProblemData, mesh, 1.e-2)

    print("CompressOperator done")

    collectionProblemData.SaveState("mordicusState")



    #################################################################
    ### ONLINE
    #################################################################

    collectionProblemData = CollectionProblemData.LoadState("mordicusState")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    snapshotCorrelationOperator = collectionProblemData.GetSnapshotCorrelationOperator("T")
    reducedOrderBasisT = collectionProblemData.GetReducedOrderBasis("T")


    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = ProblemData.ProblemData(os.path.relpath(folder))

    timeSequence = inputReader.ReadInputTimeSequence()

    constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
    #onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)

    loadingList = inputReader.ConstructLoadingsList()
    for loading in loadingList:
        loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasisT, snapshotCorrelationOperator, operatorCompressionData)
    #onlineProblemData.AddLoading(loadingList)

    onlineCompressedSolution = Th.ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasisT, operatorCompressionData, 1.e-4)

    print("check T")
    for time in onlineCompressedSolution.keys():
        print("time =", time)
        exact = solutionT.GetSnapshotAtTime(time)
        normExact = np.linalg.norm(exact)
        reconstructed = np.dot(reducedOrderBasisT.T, onlineCompressedSolution[time])
        relError = np.linalg.norm(reconstructed - exact)
        if normExact > 0:
            relError /= normExact
        print("relError = ", relError)
        print("==")


    os.system("rm -rf mordicusState.pkl")

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover

