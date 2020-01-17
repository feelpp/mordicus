# -*- coding: utf-8 -*-
import numpy as np
import os
from mpi4py import MPI
import collections
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA
from Mordicus.Modules.Safran.BasicAlgorithms import EIM


"""
Description of operatorCompressionData: dict of keys

#Offline generate:
- reducedIntegrationPoints
- reducedIntegrationWeights
- reducedListOTags
- etoIntForces, shape: len(reducedIntegrationPoints),numberOfModes,sigmaNumberOfComponents
- reducedRedInterpolator
- gappyModesAtRedIntegPt

#Online generated :
- reducedListOfConstitutiveLawTags
- statevIntForces
- statevIntForcesTemp
- stranIntForces0
- stranIntForces
- temperatureAtReducedIntegrationPoints0
- temperatureAtReducedIntegrationPoints
#### -> étapes à ajouter pour l'output des données duales:
# >>>>>> dualVarOutput et dualVarOutputNames : a changer !!! (dict ?)
- dualVarOutputNames
- dualVarOutput: collections.OrderedDict; keys:time : values: np.ndarray of size (nReducedIntegrationPoints, 2*nbeDualComponents+maxNstatv)
- sigIntForces 
- stranIntForces
"""





def PrepareOnline(onlineProblemData, timeSequence, reducedOrderBasis, operatorCompressionData):
    """
    1.
    """
    
    constitutiveLawTags = []
    maxNstatv = 0
    for key, law in onlineProblemData.GetConstitutiveLaws().items():
        if law.GetOneConstitutiveLawVariable("nstatv") >= maxNstatv:
            key0 = key
        constitutiveLawTags.append(key)
        
    maxNstatv = onlineProblemData.GetConstitutiveLaws()[key0].GetOneConstitutiveLawVariable("nstatv")
    dualVarOutputNames = onlineProblemData.GetConstitutiveLaws()[key0].GetOneConstitutiveLawVariable("var")
    
    setConstLawTag = set(constitutiveLawTags)
    assert len(constitutiveLawTags) == len(setConstLawTag), "more than one constitutive law for one element set"
    operatorCompressionData["reducedListOfConstitutiveLawTags"] = []
    for listOfTags in operatorCompressionData["reducedListOTags"]:

        listIntersec = list(setConstLawTag & set(listOfTags))
        assert len(listIntersec) == 1, "more than one constitutive law for a reducedIntegrationPoint"
        operatorCompressionData["reducedListOfConstitutiveLawTags"].append(listIntersec[0])
        

    if ('temperature', 'ALLNODE') in onlineProblemData.loadings:

        temperatureAtReducedIntegrationPoints = onlineProblemData.loadings[('temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(timeSequence[0])        
        
        operatorCompressionData["temperatureAtReducedIntegrationPoints"] = temperatureAtReducedIntegrationPoints
        
        
    nReducedIntegrationPoints = operatorCompressionData["etoIntForces"].shape[0]
    nSigmaComponents = operatorCompressionData["etoIntForces"].shape[2]
    
    operatorCompressionData["statevIntForces"] = np.zeros((nReducedIntegrationPoints,maxNstatv))
    operatorCompressionData["statevIntForcesTemp"] = np.zeros((nReducedIntegrationPoints,maxNstatv))
    operatorCompressionData["stranIntForces0"] =  np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    operatorCompressionData["stranIntForces"] = np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    operatorCompressionData["sigIntForces"] =  np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    operatorCompressionData["dualVarOutputNames"] = dualVarOutputNames
    operatorCompressionData["dualVarOutput"] = collections.OrderedDict()
    

    #update for inhomogeneous initial condition
    onlineCompressedSolution = collections.OrderedDict()
    for time in timeSequence:
        onlineCompressedSolution[time] = np.zeros(reducedOrderBasis.shape[0])


    return onlineCompressedSolution




def ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasis, operatorCompressionData, tolerance):
    """
    Compute the online stage using the method POD and ECM for a mechanical problem
    
    The parameters must have been initialized in onlineProblemData
    """
    
    
    currentFolder = os.getcwd()
    folder = currentFolder + os.sep + onlineProblemData.GetDataFolder()
    os.chdir(folder)
    
    
    onlineCompressedSolution = PrepareOnline(onlineProblemData, timeSequence, reducedOrderBasis, operatorCompressionData)
    
    for timeStep in range(1, len(timeSequence)):
        
        previousTime = timeSequence[timeStep-1]
        time = timeSequence[timeStep]
        dtime = time - previousTime
        
        #mettre dans une fonction prepareTimeIteration ?    
        for law in onlineProblemData.GetConstitutiveLaws().values():
            law.SetOneConstitutiveLawVariable('dtime', dtime)        

        if ('temperature', 'ALLNODE') in onlineProblemData.loadings:
            operatorCompressionData["temperatureAtReducedIntegrationPoints0"] = onlineProblemData.loadings[('temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time-dtime)
            
            operatorCompressionData["temperatureAtReducedIntegrationPoints"] = onlineProblemData.loadings[('temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time)        
        

        print("time =", time)
        
        reducedExternalForcesTemp = ComputeReducedExternalForces(onlineProblemData, time)
        reducedExternalForces = np.zeros(reducedExternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedExternalForcesTemp,  MPI.DOUBLE], [reducedExternalForces,  MPI.DOUBLE])
        
        normExt = np.linalg.norm(reducedExternalForces)

        before = onlineCompressedSolution[previousTime]# np.copy in niROM
        after = before# np.copy in niROM
        
        onlineCompressedSolution[time] = np.copy(before)
        
        reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, operatorCompressionData, before, after)
        reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])

        
        if normExt>0:
            normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
        else:
            normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces) # pragma: no cover
        print("normRes  =", normRes)

        count = 0
        while normRes > tolerance:
            
            reducedTangentMatrix = np.zeros(reducedTangentMatrixTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedTangentMatrixTemp,  MPI.DOUBLE], [reducedTangentMatrix,  MPI.DOUBLE])  
            
            sol = np.linalg.solve(reducedTangentMatrix, reducedExternalForces-reducedInternalForces)
            
            onlineCompressedSolution[time] += sol
            
            after = onlineCompressedSolution[time]# np.copy in niROM
            
            reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, operatorCompressionData, before, after)

            reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])

            if normExt>0:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
            else:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)# pragma: no cover
                
            print("normRes  =", normRes)
            
            
            count += 1
            if count == 20:
                raise("problem could not converge after 20 iterations") # pragma: no cover
        
        
        #mettre dans une fonction concludeTimeIteration ?  
        #solution is set
        #update Internal Variables:
        operatorCompressionData['statevIntForces'] = np.copy(operatorCompressionData['statevIntForcesTemp'])
        #set dualVarOutput:
        operatorCompressionData['dualVarOutput'][time] = np.hstack((operatorCompressionData['stranIntForces'], operatorCompressionData['sigIntForces'], operatorCompressionData['statevIntForces']))
        
        print("=== Newton iterations:", count)        

    os.chdir(currentFolder)

    
    return onlineCompressedSolution


    
def ComputeReducedExternalForces(problemData, time):

    reducedExternalForces = 0.
    for l in problemData.loadings.values():
        reducedExternalForces += l.ComputeContributionToReducedExternalForces(time)
        
    return reducedExternalForces



def ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, opCompDat, before, after):
    
    
    reducedRedInterpolator = opCompDat['reducedRedInterpolator']
    nbOfComponents = opCompDat['etoIntForces'].shape[2]

    opCompDat['sigIntForces'] = np.zeros((opCompDat['etoIntForces'].shape[0],opCompDat['etoIntForces'].shape[2]))
    
    opCompDat['stranIntForces0'] = np.tensordot(before, opCompDat['etoIntForces'], axes = (0,1))
    
    opCompDat['stranIntForces'] = np.tensordot(after, opCompDat['etoIntForces'], axes = (0,1))

    constLaws = onlineProblemData.GetConstitutiveLaws()
    
    reducedInternalForces = 0.
    reducedTangentMatrix = 0.

    #loop over integration points
    for k in range(len(opCompDat["reducedIntegrationPoints"])): 
        
        tag = opCompDat["reducedListOfConstitutiveLawTags"][k]
        
        if ('temperature', 'ALLNODE') in onlineProblemData.loadings:
            constLaws[tag].constitutiveLawVariables['temperature'] = opCompDat["temperatureAtReducedIntegrationPoints0"][k]
            
            constLaws[tag].constitutiveLawVariables['dtemp'] = opCompDat["temperatureAtReducedIntegrationPoints"][k] - opCompDat["temperatureAtReducedIntegrationPoints0"][k]
        
        constLaws[tag].constitutiveLawVariables['stran'] =  np.copy(opCompDat['stranIntForces'][k])
        
        constLaws[tag].constitutiveLawVariables['dstran'] =  opCompDat['stranIntForces'][k] - opCompDat['stranIntForces0'][k]
        
        constLaws[tag].constitutiveLawVariables['statev'] = np.copy(opCompDat['statevIntForces'][k])

        
        constLaws[tag].ComputeConstitutiveLaw()

        
        opCompDat['statevIntForcesTemp'][k]  = constLaws[tag].constitutiveLawVariables['statev']
        
        #for dualVar output
        opCompDat['sigIntForces'][k] = constLaws[tag].constitutiveLawVariables['stress']
        opCompDat['stranIntForces'][k] = constLaws[tag].constitutiveLawVariables['stran']
        opCompDat['stranIntForces'][k][3:6] /= 2.
        

        sigmaEpsilon = np.dot(reducedRedInterpolator[:,nbOfComponents*k:nbOfComponents*(k+1)],constLaws[tag].constitutiveLawVariables['stress'])
        edsdee = np.dot(np.dot(reducedRedInterpolator[:,nbOfComponents*k:nbOfComponents*(k+1)],constLaws[tag].constitutiveLawVariables['ddsdde']),reducedRedInterpolator[:,nbOfComponents*k:nbOfComponents*(k+1)].T)
      
        reducedInternalForces += opCompDat['reducedIntegrationWeights'][k]*sigmaEpsilon
        reducedTangentMatrix += opCompDat['reducedIntegrationWeights'][k]*edsdee


    return reducedInternalForces, reducedTangentMatrix



def CompressOperator(
    collectionProblemData, mesh, tolerance, listNameDualVarOutput = [], listNameDualVarGappyIndicesforECM = []
):
    """
    Operator Compression for the POD and ECM for a mechanical problem
    
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object 
    mesh : MeshBase
        mesh
    tolerance : float
        tolerance for Empirical Cubature Method
    listNameDualVarOutput : list of strings
        names of dual quantities to reconstruct on complete mesh
    listNameDualVarGappyIndicesforECM : list of strings
        names of dual quantities for which the indices of the POD are added to the reduced integration points list
                
    Returns
    -------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    """
    #BIEN APPELER "U", "sigma" et "epsilon" les quantités correspondantes
    
    #numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    #numberOfSigmaSnapshots = collectionProblemData.GetGlobalNumberOfSnapshots("sigma")
    
    
    print("ComputeMecaIntegrator...")
    integrationWeights, integrator = FT.ComputeMecaIntegrator(mesh)
    
    
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
    redIntegrator = integrator.T.dot(reducedOrderBasis.T).T
    
    
    imposedIndices = []
    for name in listNameDualVarGappyIndicesforECM:
        print("name =", name)
        imposedIndices += list(EIM.QDEIM(collectionProblemData.GetReducedOrderBasis(name)))

    imposedIndices = list(set(imposedIndices))
    
    sigmaEpsilon = ComputeSigmaEpsilon(collectionProblemData, redIntegrator)
    
    reducedIntegrationPoints, reducedIntegrationWeights = NNOMPA.ComputeReducedIntegrationScheme(integrationWeights, sigmaEpsilon, tolerance, imposedIndices = imposedIndices)
    
    #reducedIntegrationPoints = np.load("reducedIntegrationPoints.npy")
    #reducedIntegrationWeights = np.load("reducedIntegrationWeights.npy")

    sigmaNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    indices = np.array([np.arange(sigmaNumberOfComponents*i,sigmaNumberOfComponents*(i+1)) for i in reducedIntegrationPoints]).flatten()
    reducedRedInterpolator = redIntegrator[:,indices]   
    
    etoIntForces, reducedListOTags = PrecomputeReducedMaterialVariable(collectionProblemData, mesh, reducedIntegrationPoints)
    
    gappyModesAtRedIntegPts = {}
    for name in listNameDualVarOutput:
        gappyModesAtRedIntegPts[name] = collectionProblemData.GetReducedOrderBasis(name)[:,reducedIntegrationPoints]


    operatorCompressionData = {}
    operatorCompressionData["reducedIntegrationPoints"] = reducedIntegrationPoints
    operatorCompressionData["reducedIntegrationWeights"] = reducedIntegrationWeights
    operatorCompressionData["etoIntForces"] = etoIntForces
    operatorCompressionData["reducedListOTags"] = reducedListOTags
    operatorCompressionData["reducedRedInterpolator"] = reducedRedInterpolator
    operatorCompressionData["gappyModesAtRedIntegPts"] = gappyModesAtRedIntegPts
    
    collectionProblemData.SetOperatorCompressionData(operatorCompressionData)



def ComputeSigmaEpsilon(collectionProblemData, redIntegrator):
    
    """
    computes sigma(u_i):epsilon(Psi)(x_k)
    """

    sigmaNumberOfSnapshotsMinus1 = collectionProblemData.GetGlobalNumberOfSnapshots("sigma")-1
    sigmaNumberOfDofs = collectionProblemData.GetSolutionsNumberOfDofs("sigma")
    sigmaNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    numberOfIntegrationPoints = sigmaNumberOfDofs//sigmaNumberOfComponents
    
    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")

    sigmaEpsilon = np.zeros((numberOfModes*sigmaNumberOfSnapshotsMinus1,numberOfIntegrationPoints))
    redIntegrator.shape = (numberOfModes,numberOfIntegrationPoints,sigmaNumberOfComponents)


    snapshotsIteratorSigma = collectionProblemData.SnapshotsIterator("sigma", skipFirst = True)
    
    count = 0
    for sigma in snapshotsIteratorSigma:
        sigma.shape = (sigmaNumberOfComponents,numberOfIntegrationPoints)
        for j in range(numberOfIntegrationPoints):
            sigmaEpsilon[count:count+numberOfModes,j] = np.dot(redIntegrator[:,j,:],sigma[:,j]).T.flatten()
        count += numberOfModes
        sigma.shape = (sigmaNumberOfDofs)

    redIntegrator.shape = (numberOfModes,numberOfIntegrationPoints*sigmaNumberOfComponents)

    return sigmaEpsilon






def PrecomputeReducedMaterialVariable(collectionProblemData, mesh, reducedIntegrationPoints):


    uNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("U")
    sigmaNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    
    FEInterpAtIntegPointGradMatrix = FT.ComputeFEInterpGradMatAtGaussPoint(mesh)


    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
    
    componentReducedOrderBasis = []
    for i in range(uNumberOfComponents):
        componentReducedOrderBasis.append(reducedOrderBasis[:,i*numberOfNodes:(i+1)*numberOfNodes].T)

    etoIntForces = np.empty(((len(reducedIntegrationPoints),numberOfModes,sigmaNumberOfComponents)))
    #a renommer plus tard

    count = 0
    for i in range(uNumberOfComponents):
        
        etoIntForces[:,:,count] = FEInterpAtIntegPointGradMatrix[i].dot(componentReducedOrderBasis[i])[reducedIntegrationPoints,:]
        count += 1
        
    
    for i in range(uNumberOfComponents):
        for j in range(i+1,uNumberOfComponents):
            etoIntForces[:,:,count] = (FEInterpAtIntegPointGradMatrix[i].dot(componentReducedOrderBasis[j]) + FEInterpAtIntegPointGradMatrix[j].dot(componentReducedOrderBasis[i]))[reducedIntegrationPoints,:]
            count += 1
    
    
    listOfTags = FT.ComputeIntegrationPointsTags(mesh, uNumberOfComponents)
    reducedListOTags = [listOfTags[intPoint] for intPoint in reducedIntegrationPoints]
    for i, listOfTags in enumerate(reducedListOTags):
        #if not listOfTags:
        reducedListOTags[i].append("ALLELEMENT")
        
        
    return etoIntForces, reducedListOTags
