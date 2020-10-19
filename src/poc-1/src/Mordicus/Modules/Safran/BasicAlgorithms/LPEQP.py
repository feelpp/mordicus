# -*- coding: utf-8 -*-

import numpy as np
from scipy.optimize import linprog as lp


def LPEQP(integrationWeights, integrands, integrals, normIntegrals, tolerance,\
          reducedIntegrationPointsInitSet):
    """
    Linear Programming Empirical Quadrature Procedure [1].

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

    integrals : np.ndarray
        of size (numberOfIntegrands,), dtype = float.
        High-fidelity integral computed using the truth integration scheme       
    
    tolerance : float
        upper bound for the accuracy of the reduced integration scheme on the
        provided integrands
                
    Returns
    -------
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = int
        indices of the kepts integration points (reducedIntegrationPoints)
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = float
        weights associated to the kepts integration points
        (reducedIntegrationWeights)

    References
    ----------
        [1] M. Yano and A. T. Patera. An LP empirical quadrature procedure for
        reduced basis treatment of parametrized nonlinear PDEs, 2017.
        URL: https://www.researchgate.net/publication/323633428_An_LP_empirical
        _quadrature_procedure_for_reduced_basis_treatment_of_parametrized_nonli
        near_PDEs.
    """    

    method = 'simplex'

    c = np.ones(integrationWeights.shape[0])
    A_ub = np.vstack((integrands, -integrands))
    b_ub = np.hstack((tolerance*normIntegrals + integrals,\
                      tolerance*normIntegrals - integrals))
        
    if method!='revised simplex' or len(reducedIntegrationPointsInitSet) == 0:
        reducedIntegrationPointsInitSet = None
        
    optimRes = lp(c, A_ub = A_ub, b_ub = b_ub, method = method,\
                  x0 = reducedIntegrationPointsInitSet)
      
    x = optimRes['x']
    
    indices = x>1.e-10
    x = x[indices]
    s = np.where(indices)[0]                

    return s, x