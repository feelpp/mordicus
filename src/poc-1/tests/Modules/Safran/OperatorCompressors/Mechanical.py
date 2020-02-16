# -*- coding: utf-8 -*-
import numpy as np
import os
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical as Meca
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
    collectionProblemData.AddProblemData(problemData)


    print("ComputeL2ScalarProducMatrix...")
    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)

    reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-3)
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)

    reducedOrderBasisEvrcum = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "evrcum", 1.e-3)
    collectionProblemData.AddReducedOrderBasis("evrcum", reducedOrderBasisEvrcum)


    Meca.CompressOperator(collectionProblemData, mesh, 1.e-3, listNameDualVarOutput = ["evrcum"], listNameDualVarGappyIndicesforECM = ["evrcum"])

    print("CompressOperator done")

    collectionProblemData.SaveState("mordicusState")



    #################################################################
    ### ONLINE
    #################################################################

    collectionProblemData = CollectionProblemData.LoadState("mordicusState")

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    snapshotCorrelationOperator = collectionProblemData.GetSnapshotCorrelationOperator("U")
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

    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)

    from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP

    import collections
    onlineEvrcumCompressedSolution = collections.OrderedDict()
    index = operatorCompressionData['dualVarOutputNames'].index('evrcum')
    ModesAtMask = operatorCompressionData['gappyModesAtRedIntegPts']['evrcum']
    for time in operatorCompressionData['dualVarOutput'].keys():
        fieldAtMask = operatorCompressionData['dualVarOutput'][time][:,index]
        onlineEvrcumCompressedSolution[time] = GP.Fit(ModesAtMask, fieldAtMask)



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


    """from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
    reducedOrderBasisSig11 = collectionProblemData.GetReducedOrderBasis("evrcum")
    PW.WritePXDMF(mesh, onlineEvrcumCompressedSolution, reducedOrderBasisSig11, "evrcum")"""

    from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import TestMecaConstitutiveLaw as TMCL
    elasConsitutiveLaw = TMCL.TestMecaConstitutiveLaw('ALLELEMENT')
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)


    elasConsitutiveLaw = inputReader.ConstructOneConstitutiveLaw("elas", 'ALLELEMENT', "mechanical")
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)

    os.system("rm -rf mordicusState.pkl")

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover

