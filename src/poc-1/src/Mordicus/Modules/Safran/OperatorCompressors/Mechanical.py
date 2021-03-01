# -*- coding: utf-8 -*-

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

from mpi4py import MPI
import collections
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.OperatorCompressors import ReducedQuadratureProcedure as RQP
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
- hyperReducedIntegrator, shape: sigmaNumberOfComponents,numberOfModes,len(reducedIntegrationPoints)
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

secondOrderTensorOffDiagComponents = {1:[], 2:[(0,1)], 3:[(0,1), (1,2), (0,2)]}


def PrepareOnline(onlineProblemData, operatorCompressionData):
    """
    1.
    """

    onlineCompressionData = {}

    nReducedIntegrationPoints = operatorCompressionData["reducedEpsilonAtReducedIntegPoints"].shape[1]
    nSigmaComponents = operatorCompressionData["reducedEpsilonAtReducedIntegPoints"].shape[0]

    onlineCompressionData["stranIntForces0"] =  np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    onlineCompressionData["stranIntForces"] = np.zeros((nReducedIntegrationPoints,nSigmaComponents))
    onlineCompressionData["sigIntForces"] =  np.zeros((nReducedIntegrationPoints,nSigmaComponents))


    #keysConstitutiveLaws = set(onlineProblemData.GetConstitutiveLaws().keys())
    constitutiveLawSets = onlineProblemData.GetSetsOfConstitutiveOfType("mechanical")

    reducedListOTags = operatorCompressionData['reducedListOTags']
    IndicesOfIntegPointsPerMaterial = FT.ComputeIndicesOfIntegPointsPerMaterial(reducedListOTags, constitutiveLawSets)


    onlineCompressionData["statevIntForces"] = {}
    onlineCompressionData["statevIntForcesTemp"] = {}
    onlineCompressionData["dualVarOutputNames"] = {}
    onlineCompressionData["dualVarOutput"] = {}

    for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

        localNbIntPoints = len(intPoints)

        lawTag = ('mechanical', tag)

        law = onlineProblemData.GetConstitutiveLaws()[lawTag]

        nstatv = law.GetOneConstitutiveLawVariable("nstatv")

        onlineCompressionData["statevIntForces"][tag] = np.zeros((localNbIntPoints,nstatv))
        onlineCompressionData["statevIntForcesTemp"][tag] = np.zeros((localNbIntPoints,nstatv))
        onlineCompressionData["dualVarOutputNames"][tag] = law.GetOneConstitutiveLawVariable("var")
        onlineCompressionData["dualVarOutput"][tag] = collections.OrderedDict()


    onlineCompressionData['IndicesOfIntegPointsPerMaterial'] = IndicesOfIntegPointsPerMaterial


    onlineCompressionData['reducedIntegrationWeights'] = np.copy(operatorCompressionData['reducedIntegrationWeights'])
    onlineCompressionData['reducedEpsilonAtReducedIntegPoints'] = np.copy(operatorCompressionData['reducedEpsilonAtReducedIntegPoints'])

    onlineCompressionData['nbOfComponents'] = onlineCompressionData['reducedEpsilonAtReducedIntegPoints'].shape[0]
    onlineCompressionData['nbOfReducedIntPoints'] = len(onlineCompressionData["reducedIntegrationWeights"])

    return onlineCompressionData



def ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, tolerance):
    """
    Compute the online stage using the method POD and ECM for a mechanical problem

    The parameters must have been initialized in onlineProblemData
    """

    currentFolder = os.getcwd()
    folder = currentFolder + os.sep + onlineProblemData.GetDataFolder()
    os.chdir(folder)


    initialCondition = onlineProblemData.GetInitialCondition()

    onlineCompressedSolution = collections.OrderedDict()
    onlineCompressedSolution[timeSequence[0]] = initialCondition.GetReducedInitialSnapshot("U")


    onlineCompressionData = PrepareOnline(onlineProblemData, operatorCompressionData)
    IndicesOfIntegPointsPerMaterial = onlineCompressionData['IndicesOfIntegPointsPerMaterial']

    for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():
        onlineCompressionData['dualVarOutput'][tag][0] = np.hstack((onlineCompressionData['stranIntForces'][intPoints], onlineCompressionData['sigIntForces'][intPoints], onlineCompressionData['statevIntForces'][tag]))


    for timeStep in range(1, len(timeSequence)):

        previousTime = timeSequence[timeStep-1]
        time = timeSequence[timeStep]
        dtime = time - previousTime

        print("time =", time); sys.stdout.flush()

        reducedExternalForcesTemp = PrepareNewtonIterations(onlineProblemData, onlineCompressionData, time, dtime)
        reducedExternalForces = np.zeros(reducedExternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedExternalForcesTemp,  MPI.DOUBLE], [reducedExternalForces,  MPI.DOUBLE])

        normExt = np.linalg.norm(reducedExternalForces)

        before = onlineCompressedSolution[previousTime]# np.copy in niROM
        after = before# np.copy in niROM

        onlineCompressedSolution[time] = np.copy(before)

        reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after)
        reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
        MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])


        if normExt>0:
            normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
        else:
            normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces) # pragma: no cover
        print("normRes  =", normRes); sys.stdout.flush()

        count = 0
        while normRes > tolerance:

            reducedTangentMatrix = np.zeros(reducedTangentMatrixTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedTangentMatrixTemp,  MPI.DOUBLE], [reducedTangentMatrix,  MPI.DOUBLE])


            sol = np.linalg.solve(reducedTangentMatrix, reducedExternalForces-reducedInternalForces)

            onlineCompressedSolution[time] += sol

            after = onlineCompressedSolution[time]# np.copy in niROM

            reducedInternalForcesTemp, reducedTangentMatrixTemp = ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after)

            reducedInternalForces = np.zeros(reducedInternalForcesTemp.shape)
            MPI.COMM_WORLD.Allreduce([reducedInternalForcesTemp,  MPI.DOUBLE], [reducedInternalForces,  MPI.DOUBLE])


            if normExt>0:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)/normExt
            else:
                normRes = np.linalg.norm(reducedExternalForces-reducedInternalForces)# pragma: no cover

            print("normRes  =", normRes); sys.stdout.flush()

            count += 1
            if count == 50:
                raise RuntimeError("problem could not converge after 50 iterations") # pragma: no cover


        #solution is set: now update Internal Variables:
        for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

            onlineCompressionData['statevIntForces'][tag] = np.copy(onlineCompressionData['statevIntForcesTemp'][tag])

            onlineCompressionData['dualVarOutput'][tag][time] = np.hstack((onlineCompressionData['stranIntForces'][intPoints], onlineCompressionData['sigIntForces'][intPoints], onlineCompressionData['statevIntForces'][tag]))

        print("=== Newton iterations:", count); sys.stdout.flush()

    os.chdir(currentFolder)


    return onlineCompressedSolution, onlineCompressionData



def PrepareNewtonIterations(onlineProblemData, onlineCompressionData, time, dtime):

    for law in onlineProblemData.GetConstitutiveLaws().values():
        if law.GetType() == "mechanical":
            law.SetOneConstitutiveLawVariable('dtime', dtime)

    if ('U', 'temperature', 'ALLNODE') in onlineProblemData.loadings:
        onlineCompressionData["temperatureAtReducedIntegrationPoints0"] = onlineProblemData.loadings[('U', 'temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time-dtime)

        onlineCompressionData["temperatureAtReducedIntegrationPoints"] = onlineProblemData.loadings[('U', 'temperature', 'ALLNODE')].GetTemperatureAtReducedIntegrationPointsAtTime(time)

    reducedExternalForces = 0.
    for loading in onlineProblemData.GetLoadings().values():
        if loading.GetSolutionName() == "U":
            reducedExternalForces += loading.ComputeContributionToReducedExternalForces(time)

    return reducedExternalForces



def ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after):


    nbOfComponents = onlineCompressionData['nbOfComponents']
    nbOfReducedIntPoints = onlineCompressionData['nbOfReducedIntPoints']

    reducedIntegrationWeights = onlineCompressionData['reducedIntegrationWeights']
    reducedEpsilonAtReducedIntegPoints = onlineCompressionData['reducedEpsilonAtReducedIntegPoints']

    onlineCompressionData['sigIntForces'] = np.zeros((nbOfReducedIntPoints,nbOfComponents))
    onlineCompressionData['stranIntForces0'] = np.dot(reducedEpsilonAtReducedIntegPoints, before).T
    onlineCompressionData['stranIntForces'] = np.dot(reducedEpsilonAtReducedIntegPoints, after).T


    constLaws = onlineProblemData.GetConstitutiveLaws()


    sigma = np.empty((nbOfReducedIntPoints,nbOfComponents))


    localTgtMat = np.empty((nbOfReducedIntPoints,nbOfComponents,nbOfComponents))


    for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

        if ('U', 'temperature', 'ALLNODE') in onlineProblemData.loadings:

            temperature = onlineCompressionData["temperatureAtReducedIntegrationPoints0"][intPoints]
            dtemp = onlineCompressionData["temperatureAtReducedIntegrationPoints"][intPoints] - onlineCompressionData["temperatureAtReducedIntegrationPoints0"][intPoints]

        else:
            temperature = None  #pragma: no cover
            dtemp = None        #pragma: no cover

        stran = onlineCompressionData['stranIntForces'][intPoints]

        dstran =  onlineCompressionData['stranIntForces'][intPoints] - onlineCompressionData['stranIntForces0'][intPoints]

        statev = np.copy(onlineCompressionData['statevIntForces'][tag])

        lawTag = ('mechanical', tag)
        ddsdde, stress = constLaws[lawTag].ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)


        sigma[intPoints,:] = stress
        localTgtMat[intPoints,:,:] = ddsdde


        #for dualVar output
        onlineCompressionData['statevIntForcesTemp'][tag] = statev
        onlineCompressionData['sigIntForces'][intPoints] = stress

        #Voigt convention to invert for output of epsilon
        onlineCompressionData['stranIntForces'][intPoints,:3]  = stran[:,:3]
        onlineCompressionData['stranIntForces'][intPoints,3:6] = 0.5*stran[:,3:6]


    reducedInternalForces = np.einsum('l,mlk,lm->k', reducedIntegrationWeights, reducedEpsilonAtReducedIntegPoints, sigma, optimize = True)

    reducedTangentMatrix = np.einsum('l,mlk,lmn,nlo->ko', reducedIntegrationWeights, reducedEpsilonAtReducedIntegPoints, localTgtMat, reducedEpsilonAtReducedIntegPoints, optimize = True)

    return reducedInternalForces, reducedTangentMatrix




def PreCompressOperator(mesh):

    listOfTags = FT.ComputeIntegrationPointsTags(mesh, mesh.GetDimensionality())

    integrationWeights, gradPhiAtIntegPoint = FT.ComputeGradPhiAtIntegPoint(mesh)

    operatorPreCompressionData = {}
    operatorPreCompressionData["listOfTags"] = listOfTags

    operatorPreCompressionData["numberOfIntegrationPoints"] = len(integrationWeights)
    operatorPreCompressionData["integrationWeights"] = integrationWeights
    operatorPreCompressionData["gradPhiAtIntegPoint"] = gradPhiAtIntegPoint


    return operatorPreCompressionData




def CompressOperator(
    collectionProblemData, operatorPreCompressionData, mesh, tolerance, \
    listNameDualVarOutput = None, listNameDualVarGappyIndicesforECM = None, \
    toleranceCompressSnapshotsForRedQuad = 0., methodDualReconstruction = "GappyPOD",
    timeSequenceForDualReconstruction = None
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
        names of dual quantities for which the indices of the POD are added to
        the reduced integration points list

    Returns
    -------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    """
    #BIEN APPELER "U", "sigma" et "epsilon" les quantités correspondantes


    print("CompressOperator starting..."); sys.stdout.flush()

    if toleranceCompressSnapshotsForRedQuad > 0:
        collectionProblemData.defineQuantity("SigmaECM")

    listOfTags = operatorPreCompressionData["listOfTags"]

    integrationWeights = operatorPreCompressionData["integrationWeights"]
    gradPhiAtIntegPoint = operatorPreCompressionData["gradPhiAtIntegPoint"]
    #integrator0 = operatorPreCompressionData["integrator0"]
    numberOfIntegrationPoints = operatorPreCompressionData["numberOfIntegrationPoints"]


    #reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    #numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    #sigmaNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")

    import time
    start = time.time()
    reducedEpsilonAtIntegPoints = ReduceIntegrator(collectionProblemData, mesh, gradPhiAtIntegPoint, numberOfIntegrationPoints)


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

    sigmaEpsilon = ComputeSigmaEpsilon(collectionProblemData, reducedEpsilonAtIntegPoints, tolerance, toleranceCompressSnapshotsForRedQuad)

    print("Prepare ECM duration = "+str(time.time()-start)+" s"); sys.stdout.flush()

    reducedIntegrationPoints, reducedIntegrationWeights = RQP.ComputeReducedIntegrationScheme(integrationWeights, sigmaEpsilon, tolerance, imposedIndices = imposedIndices, reducedIntegrationPointsInitSet = operatorCompressionData["reducedIntegrationPoints"])
    #reducedIntegrationPoints, reducedIntegrationWeights = np.arange(integrationWeights.shape[0]), integrationWeights


    #hyperreduced operator
    reducedEpsilonAtReducedIntegPoints = reducedEpsilonAtIntegPoints[:,reducedIntegrationPoints,:]

    reducedListOTags = [listOfTags[intPoint] for intPoint in reducedIntegrationPoints]
    for i, listOfTags in enumerate(reducedListOTags):
        reducedListOTags[i].append("ALLELEMENT")


    dualReconstructionData = LearnDualReconstruction(collectionProblemData, listNameDualVarOutput, reducedIntegrationPoints, methodDualReconstruction, timeSequenceForDualReconstruction)


    operatorCompressionData = {}
    operatorCompressionData["reducedIntegrationPoints"] = reducedIntegrationPoints
    operatorCompressionData["reducedIntegrationWeights"] = reducedIntegrationWeights
    operatorCompressionData["reducedListOTags"] = reducedListOTags
    operatorCompressionData["reducedEpsilonAtReducedIntegPoints"] = reducedEpsilonAtReducedIntegPoints
    operatorCompressionData["dualReconstructionData"] = dualReconstructionData

    collectionProblemData.SetOperatorCompressionData(operatorCompressionData)



def ComputeSigmaEpsilon(collectionProblemData, reducedIntegrator, tolerance, toleranceCompressSnapshotsForRedQuad):

    """
    computes sigma(u_i):epsilon(Psi)(x_k)
    """

    redIntegratorShape = reducedIntegrator.shape
    sigmaNumberOfComponents = redIntegratorShape[0]
    numberOfModes = redIntegratorShape[2]
    numberOfIntegrationPoints = redIntegratorShape[1]

    snapshotsSigma = collectionProblemData.GetSnapshots("sigma", skipFirst = True)

    if toleranceCompressSnapshotsForRedQuad > 0.:

        SP.CompressData(collectionProblemData, "SigmaECM", tolerance, snapshots = snapshotsSigma)
        reducedOrderBasisSigmaEspilon = collectionProblemData.GetReducedOrderBasis("SigmaECM")

        reducedOrderBasisSigmaEspilonShape = reducedOrderBasisSigmaEspilon.shape

        numberOfSigmaModes = reducedOrderBasisSigmaEspilonShape[0]
        reducedOrderBasisSigmaEspilon.shape = (numberOfSigmaModes,sigmaNumberOfComponents,numberOfIntegrationPoints)

        sigmaEpsilon = np.einsum('mlk,pml->pkl', reducedIntegrator, reducedOrderBasisSigmaEspilon, optimize = True).reshape(numberOfModes*numberOfSigmaModes,numberOfIntegrationPoints)

        reducedOrderBasisSigmaEspilon.shape = reducedOrderBasisSigmaEspilonShape



    else:


        snapshotsSigmaShape = snapshotsSigma.shape
        numberOfSigmaSnapshots = snapshotsSigmaShape[0]

        snapshotsSigma.shape = (numberOfSigmaSnapshots,sigmaNumberOfComponents,numberOfIntegrationPoints)

        sigmaEpsilon = np.einsum('mlk,pml->pkl', reducedIntegrator, snapshotsSigma, optimize = True).reshape(numberOfModes*numberOfSigmaSnapshots,numberOfIntegrationPoints)

        snapshotsSigma.shape = snapshotsSigmaShape


    return sigmaEpsilon





def ReduceIntegrator(collectionProblemData, mesh, gradPhiAtIntegPoint, numberOfIntegrationPoints):


    uNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("U")
    sigNumberOfComponents = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes("U")

    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")

    componentReducedOrderBasis = []
    for i in range(uNumberOfComponents):
        componentReducedOrderBasis.append(reducedOrderBasis[:,i*numberOfNodes:(i+1)*numberOfNodes].T)


    reducedEpsilonAtIntegPoints = np.empty((sigNumberOfComponents, numberOfIntegrationPoints, numberOfModes))
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



def LearnDualReconstruction(collectionProblemData, listNameDualVarOutput, reducedIntegrationPoints, methodDualReconstruction, timeSequenceForDualReconstruction = None, snapshotsAtReducedIntegrationPoints = None, regressor = None, paramGrid = None):


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
            #1./0.

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



def ReconstructDualQuantity(nameDualQuantity, operatorCompressionData, onlineCompressionData, timeSequence):

    import collections

    onlineDualCompressedSolution = collections.OrderedDict()


    """nTimeSteps = np.array(timeSequence).shape[0]
    nReducedIntegrationPoints = operatorCompressionData["reducedEpsilonAtReducedIntegPoints"].shape[1]
    fieldAtMask = np.zeros((nTimeSteps, nReducedIntegrationPoints))

    localIndex = {}
    for tag in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].keys():
        if nameDualQuantity in onlineCompressionData['dualVarOutputNames'][tag]:
            localIndex[tag] = onlineCompressionData['dualVarOutputNames'][tag].index(nameDualQuantity)

    for i, time in enumerate(timeSequence):
        for tag, intPoints in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].items():
            if tag in localIndex:
                fieldAtMask[i, intPoints] = onlineCompressionData['dualVarOutput'][tag][time][:,localIndex[tag]]"""

    fieldAtMask = GetOnlineDualQuantityAtReducedIntegrationPoints(nameDualQuantity, onlineCompressionData, timeSequence)

    reconstructionResidual = []

    methodDualReconstruction = operatorCompressionData['dualReconstructionData']["methodDualReconstruction"]

    if methodDualReconstruction == "GappyPOD":
        from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP

        ModesAtMask = operatorCompressionData['dualReconstructionData'][nameDualQuantity]

        for i, time in enumerate(timeSequence):

            onlineDualCompressedSolution[time], error = GP.FitAndCost(ModesAtMask, fieldAtMask[i])
            reconstructionResidual.append(error)


    elif methodDualReconstruction == "MetaModel":

        from Mordicus.Core.BasicAlgorithms import ScikitLearnRegressor as SLR

        model   = operatorCompressionData['dualReconstructionData'][nameDualQuantity][0]
        scalerX = operatorCompressionData['dualReconstructionData'][nameDualQuantity][1]
        scalery = operatorCompressionData['dualReconstructionData'][nameDualQuantity][2]

        #xTest = np.hstack((np.array(timeSequence)[:,np.newaxis], fieldAtMask))
        xTest = fieldAtMask

        y = SLR.ComputeRegressionApproximation(model, scalerX, scalery, xTest)

        for i, time in enumerate(timeSequence):

            onlineDualCompressedSolution[time] = y[i]

    else:# pragma: no cover
        raise NameError(methodDualReconstruction+" not available")

    return onlineDualCompressedSolution, reconstructionResidual



def GetOnlineDualQuantityAtReducedIntegrationPoints(nameDualQuantity, onlineCompressionData, timeSequence):

    nTimeSteps = np.array(timeSequence).shape[0]

    nReducedIntegrationPoints = 0
    localIndex = {}
    for tag, intPoints in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].items():
        nReducedIntegrationPoints += intPoints.shape[0]
        if nameDualQuantity in onlineCompressionData['dualVarOutputNames'][tag]:
            localIndex[tag] = onlineCompressionData['dualVarOutputNames'][tag].index(nameDualQuantity)

    fieldAtMask = np.zeros((nTimeSteps, nReducedIntegrationPoints))

    for i, time in enumerate(timeSequence):
        for tag, intPoints in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].items():
            if tag in localIndex:
                fieldAtMask[i, intPoints] = onlineCompressionData['dualVarOutput'][tag][time][:,localIndex[tag]]

    return fieldAtMask


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

