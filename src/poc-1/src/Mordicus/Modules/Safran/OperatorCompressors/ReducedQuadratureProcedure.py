 # -*- coding: utf-8 -*-
import numpy as np
from BasicTools.Helpers.TextFormatHelper import TFormat
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA
from Mordicus.Modules.Safran.BasicAlgorithms import LPEQP



def ComputeReducedIntegrationScheme(integrationWeights, integrands, tolerance,\
        imposedIndices, reducedIntegrationPointsInitSet):
    """
    Parameters
    ----------
    integrationWeights : np.ndarray
        of size (numberOfIntegrationPoints,), dtype = float.
        Weights of the truth quadrature
    
    integrands : np.ndarray
        of size (numberOfIntegrands,numberOfIntegrationPoints), dtype = float.
        Functions we look to integrated accurately with fewer integration
        points. Usually, the integrands are already reduced, and
        numberOfIntegrands is the product of the number of reduced integrand
        modes and the number of modes of the ReducedOrderBasis
    
    tolerance : float
        upper bound for the accuracy of the reduced integration scheme on the
        provided integrands
    
    imposedIndices : np.ndarray
        of size (numberOfImposedIndices,), dtype = int.
        Optional.
        Indicies required to be selected in the reduced integration scheme
    
    reducedIntegrationPointsInitSet : 
        of size (numberOfInitReducedIntegratonPoints,), dtype = int.
        Optional.
        Initial guess for the indices of the reducedIntegrationScheme.
                

    Returns
    -------
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = int
        s: indices of the kepts integration points (reducedIntegrationPoints)
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = float
        x: weights associated to the kepts integration points
        (reducedIntegrationWeights)
    """

    
    
    # compute the integrations using the exact quadrature
    integrals = np.dot(integrands, integrationWeights)
    normIntegrals = np.linalg.norm(integrals)

    

    # initialise reducedIntegrationPoints
    if len(reducedIntegrationPointsInitSet) == 0:
        reducedIntegrationPointsInitSet = np.empty(0, dtype = int)
    

    # one step of LPEQP    
    s, x = LPEQP.LPEQP(integrationWeights,integrands,integrals,normIntegrals,\
                       tolerance,reducedIntegrationPointsInitSet)
    PrintReducedSchemeStatistics(s, x, integrands, integrals, normIntegrals)
    # step ended


    # one step of NNOMPA
    s, x = NNOMPA.NNOMPA(integrationWeights,integrands,integrals,normIntegrals,\
                       tolerance, s)
    PrintReducedSchemeStatistics(s, x, integrands, integrals, normIntegrals)
    # step ended


    # add imposed indices
    l1 = s.shape[0]
    s = np.array(list(s) + list(set(imposedIndices) - set(s)))
    dlength = s.shape[0] - l1
    x = np.hstack((x,np.zeros(dlength)))
            

    return s, x




def PrintReducedSchemeStatistics(s, x, integrands, integrals, normy):
    
    numberOfIntegrationPoints = integrands.shape[1]
    
    integrands_s = integrands[:,s]
    r = integrals - np.dot(integrands_s, x)
    err0 = np.linalg.norm(r)/normy

    print(TFormat.InRed("Reduced Integration Scheme Constructed:"))
    print(TFormat.InRed("Relative error = "+str(err0)+" obtained with " + \
    str(len(s))+" integration points (corresponding to " + \
    str(round(100*len(s)/numberOfIntegrationPoints, 5)) + "% of the total)"))    
    print(TFormat.InRed("L0 norm for weight vector: " + str(len(s))))
    print(TFormat.InRed("L1 norm for weight vector: " + str(np.linalg.norm(x, 1))))
    print(TFormat.InRed("L2 norm for weight vector: " + str(np.linalg.norm(x, 2))))