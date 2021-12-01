# -*- coding: utf-8 -*-
import numpy as np
import os
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical as Meca
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP
from Mordicus import GetTestDataPath
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
    snapshotCorrelationOperator = {}
    snapshotCorrelationOperator["U"] = FT.ComputeL2ScalarProducMatrix(mesh, 3)

    SP.CompressData(collectionProblemData, "U", 1.e-6, snapshotCorrelationOperator["U"])

    SP.CompressData(collectionProblemData, "evrcum", 1.e-6, compressSolutions = True)

    print("PreCompressOperator...")
    operatorPreCompressionData = Meca.PreCompressOperator(mesh)
    print("...done")

    Meca.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-5, listNameDualVarOutput = ["evrcum"], listNameDualVarGappyIndicesforECM = ["evrcum"], toleranceCompressSnapshotsForRedQuad = 1.e-5)
    Meca.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-5, listNameDualVarOutput = ["evrcum"], listNameDualVarGappyIndicesforECM = ["evrcum"])



    print("CompressOperator done")

    #SIO.SaveState("collectionProblemData", collectionProblemData)
    #SIO.SaveState("snapshotCorrelationOperator", snapshotCorrelationOperator)


    #################################################################
    ### ONLINE
    #################################################################

    #collectionProblemData = SIO.LoadState("collectionProblemData")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    #snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")
    #operatorPreCompressionData = SIO.LoadState("operatorPreCompressionData")

    reducedOrderBases = collectionProblemData.GetReducedOrderBases()


    folder = GetTestDataPath() + "Zset/MecaSequential/"

    inputFileName = folder + "cube.inp"
    inputReader = ZIR.ZsetInputReader(inputFileName)

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    onlineProblemData = ProblemData.ProblemData("Online")
    onlineProblemData.SetDataFolder(os.path.relpath(folder))

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

    onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-6)


    onlineEvrcumCompressedSolution, gappyError = Meca.ReconstructDualQuantity('evrcum', operatorCompressionData, onlineCompressionData, timeSequence = list(onlineCompressedSolution.keys())[1:])


    ##############
    # test LearnDualReconstruction

    onlineDualQuantityAtReducedIntegrationPoints = {}
    onlineDualQuantityAtReducedIntegrationPoints["evrcum"] = Meca.GetOnlineDualQuantityAtReducedIntegrationPoints("evrcum", onlineCompressionData, timeSequence)

    reducedIntegrationPoints = operatorCompressionData["reducedIntegrationPoints"]
    Meca.LearnDualReconstruction(collectionProblemData, ["evrcum"], reducedIntegrationPoints, methodDualReconstruction= "MetaModel", timeSequenceForDualReconstruction = timeSequence, snapshotsAtReducedIntegrationPoints = onlineDualQuantityAtReducedIntegrationPoints)
    Meca.LearnDualReconstruction(collectionProblemData, ["evrcum"], reducedIntegrationPoints, methodDualReconstruction= "MetaModel", timeSequenceForDualReconstruction = timeSequence, snapshotsAtReducedIntegrationPoints = None)
    dualReconstructionData = Meca.LearnDualReconstruction(collectionProblemData, ["evrcum"], reducedIntegrationPoints, methodDualReconstruction= "MetaModel", timeSequenceForDualReconstruction = None, snapshotsAtReducedIntegrationPoints = None)

    ##############

    operatorCompressionData["dualReconstructionData"] = dualReconstructionData
    onlineEvrcumCompressedSolution, gappyError = Meca.ReconstructDualQuantity('evrcum', operatorCompressionData, onlineCompressionData, timeSequence = list(onlineCompressedSolution.keys())[1:])


    solutionEvrcumExact  = Solution.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    solutionUExact = Solution.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    for t in outputTimeSequence:
        evrcum = solutionReader.ReadSnapshotComponent("evrcum", t, primality=False)
        solutionEvrcumExact.AddSnapshot(evrcum, t)
        U = solutionReader.ReadSnapshot("U", t, nbeOfComponentsPrimal, primality=True)
        solutionUExact.AddSnapshot(U, t)

    solutionEvrcumApprox = Solution.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    solutionEvrcumApprox.SetCompressedSnapshots(onlineEvrcumCompressedSolution)
    solutionEvrcumApprox.UncompressSnapshots(reducedOrderBases["evrcum"])

    solutionUApprox = Solution.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionUApprox.SetCompressedSnapshots(onlineCompressedSolution)
    solutionUApprox.UncompressSnapshots(reducedOrderBases["U"])

    ROMErrorsU = []
    ROMErrorsEvrcum = []
    for t in outputTimeSequence:
        exactSolution = solutionEvrcumExact.GetSnapshotAtTime(t)
        approxSolution = solutionEvrcumApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsEvrcum.append(relError)

        exactSolution = solutionUExact.GetSnapshotAtTime(t)
        approxSolution = solutionUApprox.GetSnapshotAtTime(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(approxSolution-exactSolution)
        ROMErrorsU.append(relError)

    print("ROMErrors U =", ROMErrorsU)
    print("ROMErrors Evrcum =", ROMErrorsEvrcum)



    from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MecaUniformLinearElasticity as MULE

    elasConsitutiveLaw = MULE.TestMecaConstitutiveLaw('ALLELEMENT', 300000., 0.3, 8.6E-09)
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-6)


    class callback():
        def CurrentTime(timeStep, time):
            print("time =", time)
        def CurrentNormRes(normRes):
            print("normRes  =", normRes)
        def CurrentNewtonIterations(count):
            print("=== Newton iterations:", count)


    elasConsitutiveLaw = inputReader.ConstructOneConstitutiveLaw("elas", 'ALLELEMENT')
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-6, callback = callback)

    os.system("rm -rf collectionProblemData.pkl")
    os.system("rm -rf snapshotCorrelationOperator.pkl")

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover

