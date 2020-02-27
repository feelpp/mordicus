# -*- coding: utf-8 -*-
import numpy as np
import os
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical as Meca
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP
from Mordicus.Core import GetTestDataPath
from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.IO import StateIO as SIO




def test():


    #################################################################
    ### OFFLINE
    #################################################################


    folder = GetTestDataPath() + "Zset/MecaSequential/"

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
    nbeOfComponentsPrimal = 3
    nbeOfComponentsDual = 6


    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()


    solutionU = Solution.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionSigma = Solution.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)
    solutionEvrcum = Solution.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)

    for time in outputTimeSequence:
        U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
        solutionU.AddSnapshot(U, time)
        sigma = solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False)
        solutionSigma.AddSnapshot(sigma, time)
        evrcum = solutionReader.ReadSnapshotComponent("evrcum", time, primality=False)
        solutionEvrcum.AddSnapshot(evrcum, time)


    problemData = ProblemData.ProblemData(folder)
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionSigma)
    problemData.AddSolution(solutionEvrcum)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.addVariabilityAxis("config", str)
    collectionProblemData.defineQuantity("U", "displacement", "m")
    collectionProblemData.defineQuantity("sigma", "stress", "Pa")
    collectionProblemData.defineQuantity("evrcum", "cumulated plasticity", "none")
    collectionProblemData.AddProblemData(problemData, config="case-1")


    print("ComputeL2ScalarProducMatrix...")
    snapshotCorrelationOperator = FT.ComputeL2ScalarProducMatrix(mesh, 3)

    SP.CompressData(collectionProblemData, "U", 1.e-6, snapshotCorrelationOperator)

    SP.CompressData(collectionProblemData, "evrcum", 1.e-6)

    print("PreCompressOperator...")
    operatorPreCompressionData = Meca.PreCompressOperator(mesh)
    print("...done")

    Meca.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-5, listNameDualVarOutput = ["evrcum"], listNameDualVarGappyIndicesforECM = ["evrcum"])

    print("CompressOperator done")

    SIO.SaveState("collectionProblemData", collectionProblemData)
    SIO.SaveState("snapshotCorrelationOperator", snapshotCorrelationOperator)


    #################################################################
    ### ONLINE
    #################################################################

    collectionProblemData = SIO.LoadState("collectionProblemData")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")
    #operatorPreCompressionData = SIO.LoadState("operatorPreCompressionData")

    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")
    reducedOrderBasisEvrcum = collectionProblemData.GetReducedOrderBasis("evrcum")


    folder = GetTestDataPath() + "Zset/MecaSequential/"

    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = ProblemData.ProblemData(os.path.relpath(folder))

    timeSequence = inputReader.ReadInputTimeSequence()

    constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
    onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)

    loadingList = inputReader.ConstructLoadingsList()
    onlineProblemData.AddLoading(loadingList)
    for loading in loadingList:
        loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasisU, operatorCompressionData)

    initialCondition = inputReader.ConstructInitialCondition()
    onlineProblemData.SetInitialCondition(initialCondition)

    initialCondition.ReduceInitialSnapshot(reducedOrderBasisU, snapshotCorrelationOperator)

    initOnlineCompressedSnapshot = initialCondition.GetReducedInitialSnapshot()

    onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-6)



    onlineEvrcumCompressedSolution = Meca.ReconstructDualQuantity('evrcum', operatorCompressionData, onlineCompressionData, timeSequence = list(onlineCompressedSolution.keys())[1:])


    solutionEvrcumExact  = Solution.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    for time in outputTimeSequence:
        evrcum = solutionReader.ReadSnapshotComponent("evrcum", time, primality=False)
        solutionEvrcumExact.AddSnapshot(evrcum, time)

    solutionEvrcumApprox = Solution.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    solutionEvrcumApprox.SetCompressedSnapshots(onlineEvrcumCompressedSolution)
    solutionEvrcumApprox.UncompressSnapshots(reducedOrderBasisEvrcum)

    ROMErrors = []
    for time in outputTimeSequence:
        exactSolution = solutionEvrcumExact.GetSnapshotAtTime(time)
        approxSolution = solutionEvrcumApprox.GetSnapshotAtTime(time)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrors.append(relError)

    print("ROMErrors =", ROMErrors)




    from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MecaUniformLinearElasticity as MULE

    elasConsitutiveLaw = MULE.TestMecaConstitutiveLaw('ALLELEMENT', 300000., 0.3, 8.6E-09)
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-6)


    elasConsitutiveLaw = inputReader.ConstructOneConstitutiveLaw("elas", 'ALLELEMENT', "mechanical")
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-6)

    os.system("rm -rf collectionProblemData.pkl")
    os.system("rm -rf snapshotCorrelationOperator.pkl")

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover

