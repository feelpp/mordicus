# -*- coding: utf-8 -*-

import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: 
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

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


        #solution is set: now update Internal Variables:
        for tag, intPoints in IndicesOfIntegPointsPerMaterial.items():

            onlineCompressionData['statevIntForces'][tag] = np.copy(onlineCompressionData['statevIntForcesTemp'][tag])

            onlineCompressionData['dualVarOutput'][tag][time] = np.hstack((onlineCompressionData['stranIntForces'][intPoints], onlineCompressionData['sigIntForces'][intPoints], onlineCompressionData['statevIntForces'][tag]))

        print("=== Newton iterations:", count)

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



def ComputeReducedInternalForcesAndTangentMatrix(onlineProblemData, opCompDat, onlineCompressionData, IndicesOfIntegPointsPerMaterial, before, after):


    reducedEpsilonAtReducedIntegPoints = opCompDat['reducedEpsilonAtReducedIntegPoints']

    nbOfComponents = opCompDat['reducedEpsilonAtReducedIntegPoints'].shape[0]
    nbOfReducedIntPoints = len(opCompDat["reducedIntegrationPoints"])

    onlineCompressionData['sigIntForces'] = np.zeros((nbOfReducedIntPoints,nbOfComponents))

    onlineCompressionData['stranIntForces0'] = np.dot(opCompDat['reducedEpsilonAtReducedIntegPoints'], before).T

    onlineCompressionData['stranIntForces'] = np.dot(opCompDat['reducedEpsilonAtReducedIntegPoints'], after).T


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


    reducedInternalForces = np.einsum('l,mlk,lm->k', opCompDat['reducedIntegrationWeights'], reducedEpsilonAtReducedIntegPoints, sigma, optimize = True)

    reducedTangentMatrix = np.einsum('l,mlk,lmn,nlo->ko', opCompDat['reducedIntegrationWeights'], reducedEpsilonAtReducedIntegPoints, localTgtMat, reducedEpsilonAtReducedIntegPoints, optimize = True)

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
    toleranceCompressSnapshotsForRedQuad = 0.
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


    print("CompressOperator starting...")

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

    print("prepare ECM duration =", time.time() - start)
    reducedIntegrationPoints, reducedIntegrationWeights = RQP.ComputeReducedIntegrationScheme(integrationWeights, sigmaEpsilon, tolerance, imposedIndices = imposedIndices, reducedIntegrationPointsInitSet = operatorCompressionData["reducedIntegrationPoints"])

    #hyperreduced operator
    reducedEpsilonAtReducedIntegPoints = reducedEpsilonAtIntegPoints[:,reducedIntegrationPoints,:]

    reducedListOTags = [listOfTags[intPoint] for intPoint in reducedIntegrationPoints]
    for i, listOfTags in enumerate(reducedListOTags):
        reducedListOTags[i].append("ALLELEMENT")

    gappyModesAtRedIntegPts = {}
    for name in listNameDualVarOutput:
        gappyModesAtRedIntegPts[name] = collectionProblemData.GetReducedOrderBasis(name)[:,reducedIntegrationPoints]


    operatorCompressionData = {}
    operatorCompressionData["reducedIntegrationPoints"] = reducedIntegrationPoints
    operatorCompressionData["reducedIntegrationWeights"] = reducedIntegrationWeights
    operatorCompressionData["reducedListOTags"] = reducedListOTags
    operatorCompressionData["reducedEpsilonAtReducedIntegPoints"] = reducedEpsilonAtReducedIntegPoints
    operatorCompressionData["gappyModesAtRedIntegPts"] = gappyModesAtRedIntegPts

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




def ReconstructDualQuantity(nameDualQuantity, operatorCompressionData, onlineCompressionData, timeSequence):


    from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP
    import collections

    onlineDualCompressedSolution = collections.OrderedDict()

    ModesAtMask = operatorCompressionData['gappyModesAtRedIntegPts'][nameDualQuantity]
    fieldAtMask = np.zeros(ModesAtMask.shape[1])

    localIndex = {}
    for tag in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].keys():
 
        if nameDualQuantity in onlineCompressionData['dualVarOutputNames'][tag]:
          localIndex[tag] = onlineCompressionData['dualVarOutputNames'][tag].index(nameDualQuantity)

    for time in timeSequence:
        for tag, intPoints in onlineCompressionData['IndicesOfIntegPointsPerMaterial'].items():
            if tag in localIndex:
                fieldAtMask[intPoints] = onlineCompressionData['dualVarOutput'][tag][time][:,localIndex[tag]]

        onlineDualCompressedSolution[time] = GP.Fit(ModesAtMask, fieldAtMask)

    return onlineDualCompressedSolution


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

