 # -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import lsq_linear as lsq_linear
from BasicTools.Helpers.TextFormatHelper import TFormat



def NNOMPA(integrationWeights, integrands, integrals, normIntegrals, tolerance,\
          reducedIntegrationPointsInitSet):
    """
    NonNegative Othogonal Matching Pursuit Algorithm [1].
    Modified with possibility to add random integration points.

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
        indices of the kepts integration points (reducedIntegrationPoints)
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = float
        weights associated to the kepts integration points
        (reducedIntegrationWeights)

    References
    ----------
        [1] J. Hernandez, M.A. Caicedo-Silva and A.F. Ferre. Dimensional hyper-
        reduction of nonlinear finite element models via empirical cubature, 
        2016.
        URL: https://www.researchgate.net/publication/309323670_Dimensional_hyp
        er-reduction_of_nonlinear_finite_element_models_via_empirical_cubature.
    """
    
    numberOfIntegrationPoints = integrands.shape[1]

    # initialization
    s = reducedIntegrationPointsInitSet
    x = 0
    r = integrals

    err = 1.1
    oldErr = 1.
    count0 = 0
    
    # iterations
    while err > tolerance:

        nRandom = 0#numberOfIntegrationPointsToSelect - len(s)
        notSelectedIndices = np.array(list((set(np.arange(numberOfIntegrationPoints))-set(s))))

        count = 0

        while err >= oldErr:
            
            ind = np.array(notSelectedIndices.shape[0]*np.random.rand(nRandom),\
                           dtype = int)
                
            addIndices = notSelectedIndices[ind]
            tau = np.argmax(np.dot(integrands.T,r))
            sTemp = np.array(list(s) + list(set(addIndices) - set(s)))
            sTemp = np.array(list(sTemp) + list(set([tau]) - set(sTemp)))
            integrands_s = integrands[:,sTemp]
  
            algo = lsq_linear(integrands_s, integrals, bounds=(0.,np.inf), method=\
                              'bvls', lsmr_tol='auto', verbose = 0, lsq_solver=\
                              'exact', max_iter = 500)
            xTemp = algo['x']
            
            count0 += 1
  
            index = list(np.nonzero(xTemp)[0])
            xTemp = xTemp[index]
            sTemp = sTemp[index]
            integrands_s = integrands[:,sTemp]
  
            r = integrals - np.dot(integrands_s, xTemp)
            err = np.linalg.norm(r)/normIntegrals
            count += 1


        s = sTemp
        x = xTemp
        oldErr = err


        print(TFormat.InBlue("Relative error = "+str(err)+" obtained with "+\
            str(len(s))+" integration points (corresponding to "+str(round(100*\
            len(s)/numberOfIntegrationPoints, 5))+"% of the total) ("+str(count)+\
            " sample(s) to decrease interpolation error)"))
        

    return s, x



