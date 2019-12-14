# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.OperatorCompressors import RandomSelectorWithDecreasingError as Selector



def CompressMecaOperator(
    collectionProblemData, mesh, tolerance
):
    """
    Computes the offline operator compression stage using the method of POD on the snapshots and a regression on the coefficients
    
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object 
    solutionName : str
        name of the solution to be treated
                
    Returns
    -------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    """
    #BIEN APPELER "U", "sigma" et "epsilon" les quantités correspondantes
    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes(
        "U"
    )
    numberOfSigmaSnapshots = collectionProblemData.GetGlobalNumberOfSnapshots("sigma")
    
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
    
    print("ComputeFEInterpMatAtGaussPoint...")
    FEInterpMats = FT.ComputeFEInterpMatAtGaussPoint(mesh)

    print("ComputeMecaIntegrator...")
    integrationWeights, integrator = FT.ComputeMecaIntegrator(mesh)
    
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
    redIntegrator = integrator.T.dot(reducedOrderBasis.T).T
    
    numberOfIntegrationPoints = len(integrationWeights)
    
    sigmaEpsilon = ComputeSigmaEpsilon(collectionProblemData, redIntegrator, numberOfIntegrationPoints)
    
    reducedIntegrationPoints, reducedIntegrationWeights = Selector.ComputeReducedIntegrationScheme(integrationWeights, sigmaEpsilon, tolerance)
    
    return 1.0


def ComputeSigmaEpsilon(collectionProblemData, redIntegrator, numberOfIntegrationPoints):
    """
    computes \sigma(u_i):\epsilon(\Psi)(x_k)
    ATTENTION: verifier s'il ne faut pas restaurer les "shapes"
    """

    snapshotsIteratorSigma = collectionProblemData.SnapshotsIterator("sigma")
    
    numberOfSnapshots = 0
    for sigma in snapshotsIteratorSigma:
        numberOfSnapshots += 1
    numberOfComponentsDualTensor = sigma.shape[0]//numberOfIntegrationPoints
    
    numberOfModes = collectionProblemData.GetReducedOrderBasis("U").shape[0]
    sigmaEpsilon = np.zeros((numberOfModes*numberOfSnapshots,numberOfIntegrationPoints))

    redIntegrator.shape = (numberOfModes,numberOfIntegrationPoints,numberOfComponentsDualTensor)
    
    count = 0
    for sigma in snapshotsIteratorSigma:
        sigma.shape = (numberOfIntegrationPoints,numberOfComponentsDualTensor)
        for j in range(numberOfIntegrationPoints):
            sigmaEpsilon[count:count+numberOfModes,j] = np.dot(redIntegrator[:,j,:],sigma[j,:]).T.flatten()
            
    return sigmaEpsilon


   
   
