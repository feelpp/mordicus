# -*- coding: utf-8 -*-
import numpy as np
import os
from mpi4py import MPI
import collections
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA
from Mordicus.Modules.Safran.BasicAlgorithms import EIM
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP


"""

#### Description of 'operatorPreCompressionData': dict of keys

#PreCompress generated:

- listOfTags

- integrationWeights
- integrator


#### Description of 'operatorCompressionData': dict of keys

#Compress generated:

- reducedIntegrationPoints
- reducedIntegrationWeights
- reducedListOTags
- etoIntForces, shape: len(reducedIntegrationPoints),numberOfModes,sigmaNumberOfComponents
- reducedRedInterpolator
- gappyModesAtRedIntegPt


#### Description of 'onlineCompressionData': dict of keys

#Online generated :

- reducedListOfConstitutiveLawTags
- statevIntForces
- statevIntForcesTemp
- stranIntForces0
- stranIntForces
- sigIntForces
- dualVarOutputNames
- dualVarOutput: collections.OrderedDict; keys:time : values: np.ndarray of size (nReducedIntegrationPoints, 2*nbeDualComponents+maxNstatv
- temperatureAtReducedIntegrationPoints0
- temperatureAtReducedIntegrationPoints

"""

etoIntForcesOffDiagComponents = {1:[], 2:[(0,1)], 3:[(0,1), (1,2), (0,2)]}



def PrepareOnline(onlineProblemData, operatorCompressionData):
    """
    1.
    """

    onlineCompressionData = {}

    nReducedIntegrationPoints = operatorCompressionData["etoIntForces"].shape[0]
    nSigmaComponents = operatorCompressionData["etoIntForces"].shape[2]

    onlineCompressionData["stranIntForces0"] =  np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    onlineCompressionData["stranIntForces"] = np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    onlineCompressionData["sigIntForces"] =  np.zeros((nReducedIntegrationPoints,nSigmaComponents))


    keysConstitutiveLaws = set(onlineProblemData.GetConstitutiveLaws().keys())

    reducedListOTags = operatorCompressionData['reducedListOTags']
    IndicesOfIntegPointsPerMaterial = ComputeIndicesOfIntegPointsPerMaterial(reducedListOTags, keysConstitutiveLaws)


    onlineCompressionData["statevIntForces"] = {}
    onlineCompressionData["statevIntForcesTemp"] = {}
    onlineCompressionData["dualVarOutputNames"] = {}
    onlineCompressionData["dualVarOutput"] = {}

    for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

        localNbIntPoints = len(intPoints)

        law = onlineProblemData.GetConstitutiveLaws()[tag]

        nstatv = law.GetOneConstitutiveLawVariable("nstatv")

        onlineCompressionData["statevIntForces"][tag] = np.zeros((localNbIntPoints,nstatv))
        onlineCompressionData["statevIntForcesTemp"][tag] = np.zeros((localNbIntPoints,nstatv))
        onlineCompressionData["dualVarOutputNames"][tag] = law.GetOneConstitutiveLawVariable("var")
        onlineCompressionData["dualVarOutput"][tag] = collections.OrderedDict()


    onlineCompressionData['IndicesOfIntegPointsPerMaterial'] = IndicesOfIntegPointsPerMaterial

    return onlineCompressionData



def ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasis, operatorCompressionData, tolerance):
    """
    Compute the online stage using the method POD and ECM for a mechanical problem

    The parameters must have been initialized in onlineProblemData
    """

    currentFolder = os.getcwd()
    folder = currentFolder + os.sep + onlineProblemData.GetDataFolder()
    os.chdir(folder)

    onlineCompressedSolution = collections.OrderedDict()
    onlineCompressedSolution[timeSequence[0]] = initOnlineCompressedSnapshot


    onlineCompressionData = PrepareOnline(onlineProblemData, operatorCompressionData)
    IndicesOfIntegPointsPerMaterial = onlineCompressionData['IndicesOfIntegPointsPerMaterial']



    for timeStep in range(1, len(timeSequence)):

        previousTime = timeSequence[timeStep-1]
        time = timeSequence[timeStep]
        dtime = time - previousTime

        print("time =", time)

        reducedExternalForcesTemp = PrepareNewtonIterations(onlineProblemData, onlineCompressionData, time, dtime)
        reducedExternalForces = np.zeros(reducedExternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedExternalForcesTemp,  MPI.DOUBLE], [reducedExternalForces,  MPI.DOUBLE])

        normExt = np.linalg.norm(reducedExternalForces)

        before = onlineCompressedSolution[previousTime]# np.copy in niROM
        after = before# np.copy in niROM

        onlineCompressedSolution[time] = np.copy(before)

        reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, operatorCompressionData, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after)
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

            reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, operatorCompressionData, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after)

            reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])


            if normExt>0:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
            else:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)# pragma: no cover

            print("normRes  =", normRes)

            count += 1
            if count == 20:
                raise RuntimeError("problem could not converge after 20 iterations") # pragma: no cover


        #solution is set: nowupdate Internal Variables:
        for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

            onlineCompressionData['statevIntForces'][tag] = np.copy(onlineCompressionData['statevIntForcesTemp'][tag])

            onlineCompressionData['dualVarOutput'][tag][time] = np.hstack((onlineCompressionData['stranIntForces'][intPoints], onlineCompressionData['sigIntForces'][intPoints], onlineCompressionData['statevIntForces'][tag]))

        print("=== Newton iterations:", count)

    os.chdir(currentFolder)


    return onlineCompressedSolution, onlineCompressionData



def PrepareNewtonIterations(onlineProblemData, onlineCompressionData, time, dtime):

    for law in onlineProblemData.GetConstitutiveLaws().values():
        law.SetOneConstitutiveLawVariable('dtime', dtime)

    if ('temperature', 'ALLNODE') in onlineProblemData.loadings:
        onlineCompressionData["temperatureAtReducedIntegrationPoints0"] = onlineProblemData.loadings[('temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time-dtime)

        onlineCompressionData["temperatureAtReducedIntegrationPoints"] = onlineProblemData.loadings[('temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time)

    reducedExternalForces = 0.
    for l in onlineProblemData.loadings.values():
        reducedExternalForces += l.ComputeContributionToReducedExternalForces(time)

    return reducedExternalForces



def ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, opCompDat, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after):


    reducedRedInterpolator = opCompDat['reducedRedInterpolator']
    nbOfComponents = opCompDat['etoIntForces'].shape[2]
    nbOfReducedIntPoints = len(opCompDat["reducedIntegrationPoints"])

    onlineCompressionData['sigIntForces'] = np.zeros((opCompDat['etoIntForces'].shape[0],opCompDat['etoIntForces'].shape[2]))

    onlineCompressionData['stranIntForces0'] = np.tensordot(before, opCompDat['etoIntForces'], axes = (0,1))

    onlineCompressionData['stranIntForces'] = np.tensordot(after, opCompDat['etoIntForces'], axes = (0,1))

    constLaws = onlineProblemData.GetConstitutiveLaws()


    sigma = np.empty((nbOfReducedIntPoints,nbOfComponents))
    localTgtMat = np.empty((nbOfReducedIntPoints,nbOfComponents,nbOfComponents))


    for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

        if ('temperature', 'ALLNODE') in onlineProblemData.loadings:

            temperature = onlineCompressionData["temperatureAtReducedIntegrationPoints0"][intPoints]
            dtemp = onlineCompressionData["temperatureAtReducedIntegrationPoints"][intPoints] - onlineCompressionData["temperatureAtReducedIntegrationPoints0"][intPoints]

        else:
            temperature = None  #pragma: no cover
            dtemp = None  #pragma: no cover

        stran = onlineCompressionData['stranIntForces'][intPoints]

        dstran =  onlineCompressionData['stranIntForces'][intPoints] - onlineCompressionData['stranIntForces0'][intPoints]

        statev = np.copy(onlineCompressionData['statevIntForces'][tag])


        ddsdde, stress = constLaws[tag].ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)


        sigma[intPoints,:] = stress
        localTgtMat[intPoints,:,:] = ddsdde


        #for dualVar output
        onlineCompressionData['statevIntForcesTemp'][tag] = statev
        onlineCompressionData['sigIntForces'][intPoints] = stress

        #Voigt convention to invert for output of epsilon
        onlineCompressionData['stranIntForces'][intPoints,:3]  = stran[:,:3]
        onlineCompressionData['stranIntForces'][intPoints,3:6] = 0.5*stran[:,3:6]


    reducedInternalForces = np.einsum('l,klm,lm->k', opCompDat['reducedIntegrationWeights'], reducedRedInterpolator, sigma, optimize = True)

    reducedTangentMatrix = np.einsum('l,klm,lmn,oln->ko', opCompDat['reducedIntegrationWeights'], reducedRedInterpolator, localTgtMat, reducedRedInterpolator, optimize = True)

    return reducedInternalForces, reducedTangentMatrix





def PreCompressOperator(mesh):

    listOfTags = FT.ComputeIntegrationPointsTags(mesh, mesh.GetDimensionality())

    integrationWeights, integrator = FT.ComputeMecaIntegrator(mesh)

    operatorPreCompressionData = {}
    operatorPreCompressionData["listOfTags"] = listOfTags

    operatorPreCompressionData["integrationWeights"] = integrationWeights
    operatorPreCompressionData["integrator"] = integrator

    return operatorPreCompressionData




def CompressOperator(
    collectionProblemData, operatorPreCompressionData, mesh, tolerance, listNameDualVarOutput = None, listNameDualVarGappyIndicesforECM = None
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


    print("CompressOperator starting...")


    listOfTags = operatorPreCompressionData["listOfTags"]

    integrationWeights = operatorPreCompressionData["integrationWeights"]
    integrator = operatorPreCompressionData["integrator"]


    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    sigmaNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

    redIntegrator = integrator.T.dot(reducedOrderBasis.T).T.reshape((numberOfModes,numberOfIntegrationPoints,sigmaNumberOfComponents))


    if listNameDualVarOutput is None:
        listNameDualVarOutput = []# pragma: no cover

    if listNameDualVarGappyIndicesforECM is None:
        listNameDualVarGappyIndicesforECM = []# pragma: no cover

    if not operatorCompressionData:
        operatorCompressionData["reducedIntegrationPoints"] = []


    imposedIndices = []
    for name in listNameDualVarGappyIndicesforECM:
        imposedIndices += list(EIM.QDEIM(collectionProblemData.GetReducedOrderBasis(name)))
    imposedIndices = list(set(imposedIndices))



    sigmaEpsilon = ComputeSigmaEpsilon(collectionProblemData, redIntegrator, tolerance)

    reducedIntegrationPoints, reducedIntegrationWeights = NNOMPA.ComputeReducedIntegrationScheme(integrationWeights, sigmaEpsilon, tolerance, imposedIndices = imposedIndices, reducedIntegrationPointsInitSet = operatorCompressionData["reducedIntegrationPoints"])

    #reducedIntegrationPoints = np.load("reducedIntegrationPoints.npy")
    #reducedIntegrationWeights = np.load("reducedIntegrationWeights.npy")

    #indices = np.array([np.arange(sigmaNumberOfComponents*i,sigmaNumberOfComponents*(i+1)) for i in reducedIntegrationPoints]).flatten()

    reducedRedInterpolator = redIntegrator[:,reducedIntegrationPoints,:]

    uNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("U")
    listOfTags = FT.ComputeIntegrationPointsTags(mesh, uNumberOfComponents)
    etoIntForces, reducedListOTags = PrecomputeReducedMaterialVariable(collectionProblemData, mesh, listOfTags, reducedIntegrationPoints)


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



def ComputeSigmaEpsilon(collectionProblemData, redIntegrator, tolerance):

    """
    computes sigma(u_i):epsilon(Psi)(x_k)
    """

    redIntegratorShape = redIntegrator.shape
    numberOfModes = redIntegratorShape[0]
    numberOfIntegrationPoints = redIntegratorShape[1]
    sigmaNumberOfComponents = redIntegratorShape[2]

    snapshotsSigma = collectionProblemData.GetSnapshots("sigma", skipFirst = True)

    SP.CompressData(collectionProblemData, "SigmaECM", tolerance, snapshots = snapshotsSigma)
    reducedOrderBasisSigmaEspilon = collectionProblemData.GetReducedOrderBasis("SigmaECM")

    reducedOrderBasisSigmaEspilonShape = reducedOrderBasisSigmaEspilon.shape
    numberOfSigmaModes = reducedOrderBasisSigmaEspilonShape[0]
    reducedOrderBasisSigmaEspilon.shape = (numberOfSigmaModes,sigmaNumberOfComponents,numberOfIntegrationPoints)

    sigmaEpsilon = np.einsum('klm,pml->pkl', redIntegrator, reducedOrderBasisSigmaEspilon, optimize = True).reshape(numberOfModes*numberOfSigmaModes,numberOfIntegrationPoints)

    reducedOrderBasisSigmaEspilon.shape = reducedOrderBasisSigmaEspilonShape

    return sigmaEpsilon



def ComputeIndicesOfIntegPointsPerMaterial(listOfTags, keysConstitutiveLaws):
    """
    1.
    """

    numberOfIntegrationPoints = len(listOfTags)

    localTags = []
    for i in range(numberOfIntegrationPoints):
        tags = set(listOfTags[i]+["ALLELEMENT"])
        tagsIntersec = keysConstitutiveLaws & tags
        assert len(tagsIntersec) == 1, "more than one constitutive law for a reducedIntegrationPoint"
        localTags.append(tagsIntersec.pop())

    IndicesOfIntegPointsPerMaterial = {}
    arange = np.arange(numberOfIntegrationPoints)
    for key in keysConstitutiveLaws:
        IndicesOfIntegPointsPerMaterial[key] = arange[np.array(localTags) == key]

    return IndicesOfIntegPointsPerMaterial



def PrecomputeReducedMaterialVariable(collectionProblemData, mesh, listOfTags, reducedIntegrationPoints):
    """
    notation de Voigt sur epsilon: [e_11, e_22, e_33, 2e_12, 2e_23, 2e_31]
    """


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

    for ind in etoIntForcesOffDiagComponents[uNumberOfComponents]:
        i = ind[0]
        j = ind[1]
        etoIntForces[:,:,count] = (FEInterpAtIntegPointGradMatrix[i].dot(componentReducedOrderBasis[j]) + FEInterpAtIntegPointGradMatrix[j].dot(componentReducedOrderBasis[i]))[reducedIntegrationPoints,:]
        count += 1


    reducedListOTags = [listOfTags[intPoint] for intPoint in reducedIntegrationPoints]
    for i, listOfTags in enumerate(reducedListOTags):
        reducedListOTags[i].append("ALLELEMENT")


    return etoIntForces, reducedListOTags



def ReconstructDualQuantity(nameDualQuantity, operatorCompressionData, onlineCompressionData, timeSequence):


    from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP
    import collections


    onlineDualCompressedSolution = collections.OrderedDict()

    ModesAtMask = operatorCompressionData['gappyModesAtRedIntegPts'][nameDualQuantity]
    fieldAtMask = np.empty(ModesAtMask.shape[1])

    localIndex = {}
    for tag in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].keys():
        localIndex[tag] = onlineCompressionData['dualVarOutputNames'][tag].index(nameDualQuantity)

    for time in timeSequence:

        for tag, intPoints in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].items():

            fieldAtMask[intPoints] = onlineCompressionData['dualVarOutput'][tag][time][:,localIndex[tag]]

        onlineDualCompressedSolution[time] = GP.Fit(ModesAtMask, fieldAtMask)


    return onlineDualCompressedSolution


