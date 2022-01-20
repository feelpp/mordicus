# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np
import sys

from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.OperatorCompressors import ReducedQuadratureProcedure as RQP
from Mordicus.Modules.Safran.BasicAlgorithms import EIM
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP

from Mordicus.Modules.Safran.Containers.OperatorCompressionData import OperatorCompressionDataMechanical as OCDM
from Mordicus.Modules.Safran.Containers.OnlineData import OnlineDataMechanical as ODM



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
- hyperReducedIntegrator, shape: numberOfSigmaComponents,numberOfModes,len(reducedIntegrationPoints)
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
- dualVarOutput: dict; keys:time : values: np.ndarray of size (nReducedIntegrationPoints, 2*nbeDualComponents+maxNstatv
- temperatureAtReducedIntegrationPoints0
- temperatureAtReducedIntegrationPoints




'stranIntForces0',
'stranIntForces',
'sigIntForces',
'statevIntForces',
'statevIntForcesTemp',
'dualVarOutputNames',
'dualVarOutput',
'indicesOfReducedIntegPointsPerMaterial',
'reducedIntegrationWeights',
'reducedIntegrationPoints',
'reducedEpsilonAtReducedIntegPoints',
'numberOfSigmaComponents',
'nReducedIntegrationPoints',
'temperatureAtReducedIntegrationPoints0',
'temperatureAtReducedIntegrationPoints'

"""

secondOrderTensorOffDiagComponents = {1:[], 2:[(0,1)], 3:[(0,1), (1,2), (0,2)]}


def PrepareOnline(onlineProblemData, operatorCompressionData):
    """
    1.
    """


    nReducedIntegrationPoints = operatorCompressionData.GetNumberOfReducedIntegrationPoints()
    numberOfSigmaComponents = operatorCompressionData.GetNumberOfSigmaComponents()

    onlineData = ODM.OnlineDataMechanical(nReducedIntegrationPoints, numberOfSigmaComponents)


    #keysConstitutiveLaws = set(onlineProblemData.GetConstitutiveLaws().keys())
    constitutiveLawSets = onlineProblemData.GetSetsOfConstitutiveOfType("mechanical")

    reducedListOTags = operatorCompressionData.GetReducedListOTags()
    indicesOfReducedIntegPointsPerMaterial = FT.ComputeIndicesOfIntegPointsPerMaterial(reducedListOTags, constitutiveLawSets)


    for tag, reducedIntegPoints in indicesOfReducedIntegPointsPerMaterial.items():

        localNbReducedIntegPoints = len(reducedIntegPoints)

        lawTag = ('mechanical', tag)
        law = onlineProblemData.GetConstitutiveLaws()[lawTag]

        var = law.GetOneConstitutiveLawVariable("var")

        nstatv = law.GetOneConstitutiveLawVariable("nstatv")

        onlineData.InitializeMaterial(tag, var, nstatv, localNbReducedIntegPoints)


    onlineData.SetIndicesOfReducedIntegPointsPerMaterial(indicesOfReducedIntegPointsPerMaterial)

    onlineData.SetReducedData(operatorCompressionData)

    return onlineData



def ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, tolerance, onlineData = None, callback = None):
    """
    Compute the online stage using the method POD and ECM for a mechanical problem

    The parameters must have been initialized in onlineProblemData
    """

    currentFolder = os.getcwd()

    folder = currentFolder + os.sep + onlineProblemData.GetDataFolder()
    os.chdir(folder)

    if onlineData is None:
        onlineData = PrepareOnline(onlineProblemData, operatorCompressionData)


    initialCondition = onlineProblemData.GetInitialCondition()

    onlineCompressedSolution = {}
    onlineCompressedSolution[timeSequence[0]] = initialCondition.GetReducedInitialSnapshot("U")

    indicesOfReducedIntegPointsPerMaterial = onlineData.GetIndicesOfReducedIntegPointsPerMaterial()

    onlineData.UpdateInternalStateAtReducedIntegrationPoints(timeSequence[0])

    for timeStep in range(1, len(timeSequence)):

        previousTime = timeSequence[timeStep-1]
        time = timeSequence[timeStep]
        dtime = time - previousTime

        if callback == None:
            print("time =", time); sys.stdout.flush()
        else:
            callback.CurrentTime(timeStep, time)

        reducedExternalForcesTemp = PrepareNewtonIterations(onlineProblemData, onlineData, time, dtime)
        reducedExternalForces = np.zeros(reducedExternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedExternalForcesTemp,  MPI.DOUBLE], [reducedExternalForces,  MPI.DOUBLE])

        normExt = np.linalg.norm(reducedExternalForces)

        before = onlineCompressedSolution[previousTime]# np.copy in niROM
        after = before# np.copy in niROM

        onlineCompressedSolution[time] = np.copy(before)

        reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, onlineData, indicesOfReducedIntegPointsPerMaterial, before, after)
        reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])


        if normExt>0:
            normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
        else:
            normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces) # pragma: no cover

        count = 0
        while normRes > tolerance:

            reducedTangentMatrix = np.zeros(reducedTangentMatrixTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedTangentMatrixTemp,  MPI.DOUBLE], [reducedTangentMatrix,  MPI.DOUBLE])


            sol = np.linalg.solve(reducedTangentMatrix, reducedExternalForces-reducedInternalForces)

            onlineCompressedSolution[time] += sol

            after = onlineCompressedSolution[time]# np.copy in niROM

            reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, onlineData, indicesOfReducedIntegPointsPerMaterial, before, after)

            reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])


            if normExt>0:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
            else:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)# pragma: no cover

            if callback == None:
                print("normRes  =", normRes); sys.stdout.flush()
            else:
                callback.CurrentNormRes(normRes)

            count += 1
            if count == 50:
                raise RuntimeError("problem could not converge after 50 iterations") # pragma: no cover


        #solution is set: now update Internal Variables:
        onlineData.UpdateInternalStateAtReducedIntegrationPoints(time)

        constLaws = onlineProblemData.GetConstitutiveLaws()
        for tag, intPoints in indicesOfReducedIntegPointsPerMaterial.items():
            lawTag = ('mechanical', tag)
            constLaws[lawTag].UpdateInternalState()



        if callback == None:
            print("=== Newton iterations:", count); sys.stdout.flush()
        else:
            callback.CurrentNewtonIterations(count)

    os.chdir(currentFolder)


    return onlineCompressedSolution, onlineData



def PrepareNewtonIterations(onlineProblemData, onlineData, time, dtime):

    for law in onlineProblemData.GetConstitutiveLawsOfType("mechanical"):
        law.SetOneConstitutiveLawVariable('dtime', dtime)

    if ('U', 'temperature', 'ALLNODE') in onlineProblemData.loadings:

        temperatureAtReducedIntegrationPoints0 = onlineProblemData.loadings[('U', 'temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time-dtime)
        temperatureAtReducedIntegrationPoints1 = onlineProblemData.loadings[('U', 'temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time)

        onlineData.UpdateTemperatureAtReducedIntegrationPoints(temperatureAtReducedIntegrationPoints0, temperatureAtReducedIntegrationPoints1)

    reducedExternalForces = 0.
    for loading in onlineProblemData.GetLoadings().values():
        if loading.GetSolutionName() == "U":
            reducedExternalForces += loading.ComputeContributionToReducedExternalForces(time)

    return reducedExternalForces



def ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, onlineData, indicesOfReducedIntegPointsPerMaterial, before, after):


    numberOfSigmaComponents = onlineData.GetNumberOfSigmaComponents()
    nReducedIntegrationPoints = onlineData.GetNReducedIntegrationPoints()

    reducedIntegrationWeights = onlineData.GetReducedIntegrationWeights()
    reducedEpsilonAtReducedIntegPoints = onlineData.GetReducedEpsilonAtReducedIntegPoints()

    #onlineCompressionData['sigIntForces'] = np.zeros((nReducedIntegrationPoints,numberOfSigmaComponents))

    onlineData.SetStrainAtReducedIntegrationPoints0(np.dot(reducedEpsilonAtReducedIntegPoints, before).T)
    onlineData.SetStrainAtReducedIntegrationPoints1(np.dot(reducedEpsilonAtReducedIntegPoints, after).T)


    constLaws = onlineProblemData.GetConstitutiveLaws()


    sigma = np.empty((nReducedIntegrationPoints,numberOfSigmaComponents))


    localTgtMat = np.empty((nReducedIntegrationPoints,numberOfSigmaComponents,numberOfSigmaComponents))


    for tag, intPoints in indicesOfReducedIntegPointsPerMaterial.items():

        if ('U', 'temperature', 'ALLNODE') in onlineProblemData.loadings:

            temperature = onlineData.GetTemperatureAtReducedIntegrationPoints0()[intPoints]
            dtemp = onlineData.GetTemperatureAtReducedIntegrationPoints1()[intPoints] - onlineData.GetTemperatureAtReducedIntegrationPoints0()[intPoints]

        else:
            temperature = 20.+np.zeros(intPoints.shape[0])   #pragma: no cover
            dtemp = np.zeros(intPoints.shape[0])             #pragma: no cover

        stran = onlineData.GetStrainAtReducedIntegrationPoints1()[intPoints] # pas Strain0 ???

        dstran =  onlineData.GetStrainAtReducedIntegrationPoints1()[intPoints] - onlineData.GetStrainAtReducedIntegrationPoints0()[intPoints]

        statev = np.copy(onlineData.GetStateVarAtReducedIntegrationPoints0(tag))


        lawTag = ('mechanical', tag)
        ddsdde, stress, statev = constLaws[lawTag].ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)


        sigma[intPoints,:] = stress
        localTgtMat[intPoints,:,:] = ddsdde


        #for dualVar output
        onlineData.SetStateVarAtReducedIntegrationPoints1(tag, statev)
        onlineData.SetStressAtLocalReducedIntegrationPoints1(stress, intPoints)

        #Voigt convention to invert for output of epsilon
        localStrain = np.copy(stran)
        if numberOfSigmaComponents == 6:
            localStrain[:,3:6] *= 0.5
        elif numberOfSigmaComponents == 6:
            localStrain[:,3] *= 0.5
        onlineData.SetStrainAtLocalReducedIntegrationPoints1(localStrain, intPoints)


    reducedInternalForces = np.einsum('l,mlk,lm->k', reducedIntegrationWeights, reducedEpsilonAtReducedIntegPoints, sigma, optimize = True)

    reducedTangentMatrix = np.einsum('l,mlk,lmn,nlo->ko', reducedIntegrationWeights, reducedEpsilonAtReducedIntegPoints, localTgtMat, reducedEpsilonAtReducedIntegPoints, optimize = True)

    return reducedInternalForces, reducedTangentMatrix


def PreCompressOperator(collectionProblemData, mesh):
    """
    Preliminary operator compression step for the POD-ECM method for a
    mechanical problem, precomputing quantities that only depend on the mesh
    Requires naming the displacement solution "U" and the stress solution
    "sigma"

    Parameters
    ----------
    mesh: BasicToolsUnstructuredMesh
        high-dimensional mesh

    Returns
    -------
    dict
        containing precomputed quantities
    """
    listOfTags = FT.ComputeIntegrationPointsTags(mesh, mesh.GetDimensionality())

    integrationWeights, gradPhiAtIntegPoint = FT.ComputeGradPhiAtIntegPoint(mesh)

    operatorCompressionData = OCDM.OperatorCompressionDataMechanical(gradPhiAtIntegPoint, integrationWeights, listOfTags)

    collectionProblemData.SetOperatorCompressionData(operatorCompressionData)


def CompressOperator(
    collectionProblemData, mesh, tolerance, \
    listNameDualVarOutput = None, listNameDualVarGappyIndicesforECM = None, \
    toleranceCompressSnapshotsForRedQuad = 0., methodDualReconstruction = "GappyPOD",
    timeSequenceForDualReconstruction = None):
    """
    Operator compression step for the POD-ECM method for a mechanical problem
    Requires naming the displacement solution "U" and the stress solution
    "sigma"

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    operatorPreCompressionData : dict
        containing precomputed quantities, namely the quantities produced by
        the operator compression step that only depend on the mesh
    mesh: BasicToolsUnstructuredMesh
        high-dimensional mesh
    tolerance : float
        tolerance for the Empirical Cubature Method (ECM)
    listNameDualVarOutput : list of strings, optional
        names of dual quantities to reconstruct on complete mesh
    listNameDualVarGappyIndicesforECM : list of strings, optional
        names of dual quantities for which the indices of the POD are added to
        the reduced integration points list
    toleranceCompressSnapshotsForRedQuad : float, optional
        if > 0., sigma is compressed using snapshots POD before applying ECM
    methodDualReconstruction : str, optional
        method used to reconstruct the dual quantities from the reduced
        integration points to the complete mesh, "GappyPOD" or "MetaModel"
    timeSequenceForDualReconstruction : list or 1D np.ndarray, optional
        time sequence used to train the dual quantities reconstruction
        algorithm
    """

    print("CompressOperator starting..."); sys.stdout.flush()

    if toleranceCompressSnapshotsForRedQuad > 0:
        collectionProblemData.DefineQuantity("SigmaECM")


    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    listOfTags = operatorCompressionData.GetListOfTags()

    integrationWeights = operatorCompressionData.GetIntegrationWeights()
    #gradPhiAtIntegPoint = operatorCompressionData.GetGradPhiAtIntegPoint()
    #numberOfIntegrationPoints = operatorCompressionData.GetNumberOfIntegrationPoints()

    #reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")

    #numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    #numberOfSigmaComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")

    import time
    start = time.time()
    reducedEpsilonAtIntegPoints = ReduceIntegrator(collectionProblemData, mesh)



    #if listNameDualVarGappyIndicesforECM is None:
    #    listNameDualVarGappyIndicesforECM = []# pragma: no cover
    #
    #if not operatorCompressionData:
    #    operatorCompressionData["reducedIntegrationPoints"] = []



    sigmaEpsilon = ComputeSigmaEpsilon(collectionProblemData, reducedEpsilonAtIntegPoints, tolerance, toleranceCompressSnapshotsForRedQuad)


    imposedIndices = []
    for name in listNameDualVarGappyIndicesforECM:
        imposedIndices += list(EIM.QDEIM(collectionProblemData.GetReducedOrderBasis(name)))
    imposedIndices = list(set(imposedIndices))

    reducedIntegrationPointsInitSet = operatorCompressionData.GetReducedIntegrationPoints()

    print("Prepare ECM duration = "+str(time.time()-start)+" s"); sys.stdout.flush()

    reducedIntegrationPoints, reducedIntegrationWeights = RQP.ComputeReducedIntegrationScheme(integrationWeights, sigmaEpsilon, tolerance, imposedIndices = imposedIndices, reducedIntegrationPointsInitSet = reducedIntegrationPointsInitSet)
    #reducedIntegrationPoints, reducedIntegrationWeights = np.arange(integrationWeights.shape[0]), integrationWeights


    #hyperreduced operator
    #reducedEpsilonAtReducedIntegPoints = reducedEpsilonAtIntegPoints[:,reducedIntegrationPoints,:]
    reducedEpsilonAtReducedIntegPoints = HyperReduceIntegrator(reducedEpsilonAtIntegPoints, reducedIntegrationPoints)


    reducedListOTags = [listOfTags[intPoint] for intPoint in reducedIntegrationPoints]
    for i, listOfTags in enumerate(reducedListOTags):
        reducedListOTags[i].append("ALLELEMENT")


    #hyperreduce boundary conditions
    #reducedOrderBases = collectionProblemData.GetReducedOrderBases

    #integrationWeightsRadiation, phiAtIntegPointRadiation = FT.ComputePhiAtIntegPoint(mesh)
    #for _, problemData in collectionProblemData.GetProblemDatas().items():
    #    centrifugalLoading = problemData.GetLoadingsOfType('centrifugal')
    #    unAssembledReducedUnitCentrifugalVector, _ = centrifugalLoading.ReduceLoading(mesh, problemData, reducedOrderBases, integrationWeights = integrationWeightsRadiation, phiAtIntegPoint = phiAtIntegPointRadiation)"""


    dualReconstructionData = LearnDualReconstruction(collectionProblemData, listNameDualVarOutput, reducedIntegrationPoints, methodDualReconstruction, timeSequenceForDualReconstruction)

    operatorCompressionData.SetReducedIntegrationPoints(reducedIntegrationPoints)
    operatorCompressionData.SetReducedIntegrationWeights(reducedIntegrationWeights)
    operatorCompressionData.SetReducedListOTags(reducedListOTags)
    operatorCompressionData.SetReducedEpsilonAtReducedIntegPoints(reducedEpsilonAtReducedIntegPoints)
    operatorCompressionData.SetDualReconstructionData(dualReconstructionData)



def ComputeSigmaEpsilon(collectionProblemData, reducedEpsilonAtIntegPoints, tolerance, toleranceCompressSnapshotsForRedQuad):

    """
    computes sigma(u_i):epsilon(Psi)(x_k)
    """

    numberOfSigmaComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")

    numberOfIntegrationPoints = collectionProblemData.GetOperatorCompressionData().GetNumberOfIntegrationPoints()


    snapshotsSigma = collectionProblemData.GetSnapshots("sigma", skipFirst = True)

    if toleranceCompressSnapshotsForRedQuad > 0.:

        SP.CompressData(collectionProblemData, "SigmaECM", tolerance, snapshots = snapshotsSigma)
        reducedOrderBasisSigmaEspilon = collectionProblemData.GetReducedOrderBasis("SigmaECM")

        reducedOrderBasisSigmaEspilonShape = reducedOrderBasisSigmaEspilon.shape

        numberOfSigmaModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("SigmaECM")

        reducedOrderBasisSigmaEspilon.shape = (numberOfSigmaModes,numberOfSigmaComponents,numberOfIntegrationPoints)

        sigmaEpsilon = np.einsum('mlk,pml->pkl', reducedEpsilonAtIntegPoints, reducedOrderBasisSigmaEspilon, optimize = True).reshape(numberOfModes*numberOfSigmaModes,numberOfIntegrationPoints)

        reducedOrderBasisSigmaEspilon.shape = reducedOrderBasisSigmaEspilonShape


    else:

        snapshotsSigmaShape = snapshotsSigma.shape

        numberOfSigmaSnapshots = collectionProblemData.GetGlobalNumberOfSnapshots("sigma", skipFirst = True)
        snapshotsSigma.shape = (numberOfSigmaSnapshots,numberOfSigmaComponents,numberOfIntegrationPoints)

        sigmaEpsilon = np.einsum('mlk,pml->pkl', reducedEpsilonAtIntegPoints, snapshotsSigma, optimize = True).reshape(numberOfModes*numberOfSigmaSnapshots,numberOfIntegrationPoints)

        snapshotsSigma.shape = snapshotsSigmaShape


    return sigmaEpsilon



def ReduceIntegrator(collectionProblemData, mesh):
    """
    Computes the reduced integrator, named reducedEpsilonAtIntegPoints.
    epsilon(u_t)(x_k), where u_t is a test displacement and x_k are the
    integration points is called integrator, since the internal forces vector
    is obtained using sigma:epsilon(u_t)(x_k). reducedEpsilonAtIntegPoints
    denotes epsilon(Psi)(x_k), where Psi is a POD mode and x_k are the
    integration points.

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    mesh: BasicToolsUnstructuredMesh
        high-dimensional mesh
    gradPhiAtIntegPoint : scipy.sparse.coo_matrix
        of size (numberOfIntegrationPoints, numberOfModes), components of the
        gradient of the shape functions at the integration points
    numberOfIntegrationPoints : int
        number of integration points (Lagrange isoparametric finite elements)

    Returns
    -------
    np.ndarray
        of size (numberOfSigmaComponents,numberOfIntegrationPoints,numberOfModes)
    """


    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    numberOfIntegrationPoints = operatorCompressionData.GetNumberOfIntegrationPoints()
    gradPhiAtIntegPoint = operatorCompressionData.GetGradPhiAtIntegPoint()

    uNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("U")
    numberOfSigmaComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")

    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")

    componentReducedOrderBasis = []
    for i in range(uNumberOfComponents):
        componentReducedOrderBasis.append(reducedOrderBasis[:,i*numberOfNodes:(i+1)*numberOfNodes].T)


    reducedEpsilonAtIntegPoints = np.empty((numberOfSigmaComponents, numberOfIntegrationPoints, numberOfModes))
    count = 0
    for i in range(uNumberOfComponents):
        reducedEpsilonAtIntegPoints[count,:,:] = gradPhiAtIntegPoint[i].dot(componentReducedOrderBasis[i])
        count += 1

    for ind in secondOrderTensorOffDiagComponents[uNumberOfComponents]:
        i = ind[0]
        j = ind[1]
        reducedEpsilonAtIntegPoints[count,:,:] = gradPhiAtIntegPoint[i].dot(componentReducedOrderBasis[j]) + gradPhiAtIntegPoint[j].dot(componentReducedOrderBasis[i])
        count += 1

    return reducedEpsilonAtIntegPoints


def HyperReduceIntegrator(reducedEpsilonAtIntegPoints, reducedIntegrationPoints):

    return reducedEpsilonAtIntegPoints[:,reducedIntegrationPoints,:]


def LearnDualReconstruction(collectionProblemData, listNameDualVarOutput, reducedIntegrationPoints, methodDualReconstruction, timeSequenceForDualReconstruction = None, snapshotsAtReducedIntegrationPoints = None, regressor = None, paramGrid = None):
    """
    Train the agorithm of reconstruction of the dual quantities from the
    reduced integration points to the complete mesh: "GappyPOD" or "MetaModel"

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    listNameDualVarOutput : list of strings, optional
        names of dual quantities to reconstruct on complete mesh
    reducedIntegrationPoints : np.ndarray
        of size (nReducedIntegrationPoints,), dtype = int
        indices of the reduced integration points
    methodDualReconstruction : str
        method used to reconstruct the dual quantities from the reduced
        integration points to the complete mesh, "GappyPOD" or "MetaModel"
    timeSequenceForDualReconstruction : list or 1D np.ndarray, optional
        time sequence used to train the dual quantities reconstruction
        algorithm
    snapshotsAtReducedIntegrationPoints : dict, optional
        dual quantity at reduced integrationPoints, for which reconstruction is
        trained
    regressor : object satisfying the scikit-learn regressors API, optional
        regressor used for the method "MetaModel"
    paramGrid : dict, optional
        of lists (of floats) containing hyperparameter values of the considered
        regressor

    Returns
    -------
    dict
        dictionary containing data used for reconstructing dual quantities in
        the online stage, with key:values:

        "methodDualReconstruction : str
            "GappyPOD" or "MetaModel"

        name of dual quantities (e.g. "evrcum"):

            - if "MetaModel" : tuple

            model: sklearn.model_selection._search.GridSearchCV

            scalerX: sklearn.preprocessing._data.StandardScaler

            scalery: sklearn.preprocessing._data.StandardScaler

            - if "GappyPOD" : tuple

            reducedOrderBasisAtReducedIntegrationPoints: np.ndarray
            of size (numberOfModes, nReducedIntegrationPoints)

    Notes
    -----
    Regressor and paramGrid mush be both None or both specified
    """

    if listNameDualVarOutput is None:
        listNameDualVarOutput = []# pragma: no cover

    dualReconstructionData = {}

    if methodDualReconstruction == "GappyPOD":
        dualReconstructionData["methodDualReconstruction"] = "GappyPOD"
        for name in listNameDualVarOutput:
            dualReconstructionData[name] = collectionProblemData.GetReducedOrderBasis(name)[:,reducedIntegrationPoints]

    elif methodDualReconstruction == "MetaModel":
        dualReconstructionData["methodDualReconstruction"] = "MetaModel"
        for name in listNameDualVarOutput:

            print("Running MetaModel for solutionName =", name)


            if timeSequenceForDualReconstruction is None:
                solutionTimeSteps = collectionProblemData.GetSolutionTimeSteps(name, skipFirst = True)[:,np.newaxis]
                if snapshotsAtReducedIntegrationPoints is None:
                    localSnapshotsAtReducedIntegrationPoints = collectionProblemData.GetSnapshots(name, skipFirst = True)[:,reducedIntegrationPoints]
                else:# pragma: no cover
                    raise RuntimeError("cannot specify snapshotsAtReducedIntegrationPoints when timeSequenceForDualReconstruction is None")
                yTrain = collectionProblemData.GetCompressedSnapshots(name, skipFirst = True)
            else:
                solutionTimeSteps = np.array(timeSequenceForDualReconstruction)[:,np.newaxis]
                if snapshotsAtReducedIntegrationPoints is None:
                    localSnapshotsAtReducedIntegrationPoints = collectionProblemData.GetSnapshotsAtTimes(name, timeSequenceForDualReconstruction)[:,reducedIntegrationPoints]
                else:
                    localSnapshotsAtReducedIntegrationPoints = snapshotsAtReducedIntegrationPoints[name]
                yTrain = collectionProblemData.GetCompressedSnapshotsAtTimes(name, timeSequenceForDualReconstruction)
                solutionTimeSteps = np.tile(solutionTimeSteps, (collectionProblemData.GetNumberOfProblemDatas(),1))


            #print("solutionTimeSteps =", solutionTimeSteps)
            #print("localSnapshotsAtReducedIntegrationPoints =", localSnapshotsAtReducedIntegrationPoints)

            assert solutionTimeSteps.shape[0] == localSnapshotsAtReducedIntegrationPoints.shape[0], "number of time steps different from number of snapshots at reduced integration points"

            #XTrain = np.hstack((solutionTimeSteps, localSnapshotsAtReducedIntegrationPoints))
            XTrain = localSnapshotsAtReducedIntegrationPoints


            from Mordicus.Core.BasicAlgorithms import ScikitLearnRegressor as SLR

            """
            from sklearn.gaussian_process.kernels import WhiteKernel, ConstantKernel, Matern
            #from sklearn.gaussian_process import GaussianProcessRegressor
            kernel = Matern(length_scale=1., nu=2.5) + ConstantKernel(constant_value=1.0, constant_value_bounds=(0.001, 1.0)) * WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e0))
            #regressor = GaussianProcessRegressor(kernel=kernel)
            regressor = SLR.MyGPR(kernel=kernel)

            paramGrid = {'kernel__k1__length_scale': [0.1, 1., 10.], 'kernel__k1__nu':[1.5, 2.5], 'kernel__k2__k1__constant_value':[0.001, 0.01]}#, 'kernel__k2__k2__noise_level':[1, 2]}
            """

            #from pprint import pprint
            #pprint(vars(regressor))
            #print("regressor.get_params().keys() =", regressor.get_params().keys())

            if regressor is None and paramGrid is None:
                from sklearn import linear_model
                regressor = linear_model.Lasso(alpha=0.1, max_iter=1e6, tol=1e-6)
                paramGrid = {'alpha': [0.01, 0.1, 1.]}
            if (regressor is None and paramGrid is not None) or (regressor is not None and paramGrid is None):#pragma: no cover
                raise ValueError('regressor and paramGrid mush be both None or both specified')


            model, scalerX, scalery = SLR.GridSearchCVRegression(regressor, paramGrid, XTrain, yTrain)
            dualReconstructionData[name] = (model, scalerX, scalery)

    else:# pragma: no cover
        print(">> Not learning how to reconstructing dual variables")

    return dualReconstructionData


def ReconstructDualQuantity(nameDualQuantity, operatorCompressionData, onlineData, timeSequence):
    """
    Reconstruct a dual quantitie using a trained algorithm

    Parameters
    ----------
    nameDualQuantity : str
        name of the dual quantity to reconstruct
    operatorCompressionData : dict
        dictionary containing data generated by the operator compression step
        In the present case (POD-ECM), with key:values:

        "reducedIntegrationPoints": np.ndarray of size
        (nReducedIntegrationPoints,), dtype = int

        "reducedIntegrationWeights": np.ndarray of size
        (nReducedIntegrationPoints,), dtype = float

        "reducedListOTags": list of lists (of str)
        of length nReducedIntegrationPoints, containing all the tags of the
        element containing the integration points

        "reducedEpsilonAtReducedIntegPoints": np.ndarray of size
            (numberOfSigmaComponents,numberOfIntegrationPoints,numberOfModes),
            dtype = float
            contains epsilon(Psi)(x_k), where Psi is a POD mode and x_k are the
            reduced integration points

        "dualReconstructionData": dict
            dictionary containing data used for reconstructing dual quantities
            in the online stage, with key:values:

            "methodDualReconstruction : str
                "GappyPOD" or "MetaModel"

            name of dual quantities (e.g. "evrcum"):

                - if "MetaModel" : tuple

                model: sklearn.model_selection._search.GridSearchCV

                scalerX: sklearn.preprocessing._data.StandardScaler

                scalery: sklearn.preprocessing._data.StandardScaler

                - if "GappyPOD" : tuple

                reducedOrderBasisAtReducedIntegrationPoints: np.ndarray
                of size (numberOfModes, nReducedIntegrationPoints)

    onlineCompressionData : np.ndarray
        of size (nReducedIntegrationPoints,), dtype = int
        indices of the reduced integration points
    timeSequence : list or 1D np.ndarray, optional
        time sequence used to train the dual quantities reconstruction
        algorithm

    Returns
    -------
    dict
        with float as keys (time steps) and  np.ndarray of size (nbeModes,) as
        values (compressedSnapshots of the reconstructed dual quantity)
    list
        of floats, contains the resitual of the reconstruction if "GappyPOD" is
        used, empty list otherwise

    Notes
    -----
    Regressor and paramGrid mush be both None or both specified
    """

    onlineDualCompressedSolution = {}

    #nTimeSteps = np.array(timeSequence).shape[0]
    #nReducedIntegrationPoints = operatorCompressionData["reducedEpsilonAtReducedIntegPoints"].shape[1]
    #fieldAtMask = np.zeros((nTimeSteps, nReducedIntegrationPoints))
    #localIndex = {}
    #for tag in onlineCompressionData['indicesOfReducedIntegPointsPerMaterial'].keys():
    #    if nameDualQuantity in onlineCompressionData['dualVarOutputNames'][tag]:
    #        localIndex[tag] = onlineCompressionData['dualVarOutputNames'][tag].index(nameDualQuantity)
    #for i, time in enumerate(timeSequence):
    #    for tag, intPoints in onlineCompressionData['indicesOfReducedIntegPointsPerMaterial'].items():
    #        if tag in localIndex:
    #            fieldAtMask[i, intPoints] = onlineCompressionData['dualVarOutput'][tag][time][:,localIndex[tag]]

    fieldAtMask = GetOnlineDualQuantityAtReducedIntegrationPoints(nameDualQuantity, onlineData, timeSequence)
    #print(nameDualQuantity, fieldAtMask)

    reconstructionResidual = []

    methodDualReconstruction = operatorCompressionData.GetDualReconstructionData()["methodDualReconstruction"]


    if methodDualReconstruction == "GappyPOD":
        from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP

        ModesAtMask = operatorCompressionData.GetDualReconstructionData()[nameDualQuantity]

        for i, time in enumerate(timeSequence):

            onlineDualCompressedSolution[time], error = GP.FitAndCost(ModesAtMask, fieldAtMask[i])
            reconstructionResidual.append(error)


    elif methodDualReconstruction == "MetaModel":

        from Mordicus.Core.BasicAlgorithms import ScikitLearnRegressor as SLR

        model   = operatorCompressionData.GetDualReconstructionData()[nameDualQuantity][0]
        scalerX = operatorCompressionData.GetDualReconstructionData()[nameDualQuantity][1]
        scalery = operatorCompressionData.GetDualReconstructionData()[nameDualQuantity][2]

        #xTest = np.hstack((np.array(timeSequence)[:,np.newaxis], fieldAtMask))
        xTest = fieldAtMask

        y = SLR.ComputeRegressionApproximation(model, scalerX, scalery, xTest)

        for i, time in enumerate(timeSequence):

            onlineDualCompressedSolution[time] = y[i]

    else:# pragma: no cover
        raise NameError(methodDualReconstruction+" not available")

    return onlineDualCompressedSolution, reconstructionResidual


def GetOnlineDualQuantityAtReducedIntegrationPoints(nameDualQuantity, onlineData, timeSequence):

    nTimeSteps = np.array(timeSequence).shape[0]

    nReducedIntegrationPoints = 0
    localIndex = {}
    for tag, intPoints in onlineData.GetIndicesOfReducedIntegPointsPerMaterial().items():
        nReducedIntegrationPoints += intPoints.shape[0]
        if nameDualQuantity in onlineData.GetDualVarOutputNames(tag):
            localIndex[tag] = onlineData.GetDualVarOutputNames(tag).index(nameDualQuantity)

    fieldAtMask = np.zeros((nTimeSteps, nReducedIntegrationPoints))

    for i, time in enumerate(timeSequence):
        for tag, intPoints in onlineData.GetIndicesOfReducedIntegPointsPerMaterial().items():
            if tag in localIndex:
                fieldAtMask[i, intPoints] = onlineData.GetDualVarOutput(tag)[time][:,localIndex[tag]]

    return fieldAtMask


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

