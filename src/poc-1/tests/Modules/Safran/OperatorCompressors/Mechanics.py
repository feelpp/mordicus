# -*- coding: utf-8 -*-
import numpy as np
import os
from Mordicus.Modules.Safran.OperatorCompressors import Mechanics as Meca
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

    reducedOrderBasisEvrcum = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "evrcum", 1.e-2)
    collectionProblemData.AddReducedOrderBasis("evrcum", reducedOrderBasisEvrcum)


    Meca.CompressMecaOperator(collectionProblemData, mesh, 1.e-2, listNameDualVarOutput = ["evrcum"], listNameDualVarGappyIndicesforECM = ["evrcum"])
    
    print("CompressMecaOperator done")

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
        loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasisU, snapshotCorrelationOperator, operatorCompressionData)
    
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)
    
    from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP

    import collections
    onlineEvrcumCompressedSolution = collections.OrderedDict()
    index = operatorCompressionData['dualVarOutputNames'].index('evrcum')
    ModesAtMask = operatorCompressionData['gappyModesAtRedIntegPts']['evrcum']
    for time in operatorCompressionData['dualVarOutput'].keys():
        fieldAtMask = operatorCompressionData['dualVarOutput'][time][:,index]
        onlineEvrcumCompressedSolution[time] = GP.Fit(ModesAtMask, fieldAtMask)
        

    
    solutionEvrcum = Solution.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
    for time in outputTimeSequence:
        evrcum = solutionReader.ReadSnapshotComponent("evrcum", time, primality=False)
        solutionEvrcum.AddSnapshot(evrcum, time)

    print("check evrcum")
    for time in onlineEvrcumCompressedSolution.keys():
        print("time =", time)
        exact = solutionEvrcum.GetSnapshotAtTime(time)
        normExact = np.linalg.norm(exact)
        reconstructed = np.dot(reducedOrderBasisEvrcum.T, onlineEvrcumCompressedSolution[time])
        relError = np.linalg.norm(reconstructed - exact)
        if normExact > 0:
            relError /= normExact
        print("relError = ", relError)
        print("==")

    
    """from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
    reducedOrderBasisSig11 = collectionProblemData.GetReducedOrderBasis("evrcum")
    PW.WritePXDMF(mesh, onlineEvrcumCompressedSolution, reducedOrderBasisSig11, "evrcum")"""
    
    from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import TestMecaConstitutiveLaw as TMCL
    elasConsitutiveLaw = TMCL.TestMecaConstitutiveLaw('ALLELEMENT')
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4) 


    elasConsitutiveLaw = inputReader.ConstructOneConstitutiveLaw("elas", 'ALLELEMENT', "mechanical")
    onlineProblemData.AddConstitutiveLaw(elasConsitutiveLaw)
    onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)

    os.system("rm -rf mordicusState.pkl")

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover

