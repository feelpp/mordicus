# -*- coding: utf-8 -*-

import numpy as np


def LPEQP(integrationWeights, integrands, integrals, normIntegrals, tolerance):
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

    normIntegrals : float
        np.linalg.norm(integrals), already computed in mordicus use

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

    # optimization options
    optimStatus = {}
    optimStatus[0] = "Optimization proceeding nominally"
    optimStatus[1] = "Iteration limit reached"
    optimStatus[2] = "Problem appears to be infeasible"
    optimStatus[3] = "Problem appears to be unbounded"
    optimStatus[4] = "Numerical difficulties encountered"

    #method = 'revised simplex'
    method = 'interior-point'

    options = {}
    options['interior-point'] = {\
    'maxiter': 100, 'tol': 1e-06, 'disp':\
    False, 'alpha0': 0.99995, 'beta': 0.1, 'sparse': False,\
    'lstsq': False, 'sym_pos': False, 'cholesky': False, 'pc': True,\
    'ip': False, 'permc_spec': 'MMD_AT_PLUS_A', 'presolve': True}

    options['revised simplex'] = {\
    'maxiter': 100, 'tol': 1e-06, 'disp': False}


    # problem definition
    c = np.ones(integrationWeights.shape[0])
    A_ub = np.vstack((integrands, -integrands))

    b_ub = np.hstack((tolerance*normIntegrals + integrals,\
                      tolerance*normIntegrals - integrals))


    # optimization call
    optimRes = CallOptimizer(c, A_ub, b_ub, method, options[method])


    # provide result if optimization successful
    x = optimRes['x']
    print("Optimization status =", optimStatus.get(optimRes['status'], "key not known"))


    if optimRes['status'] < 2:
        # return the solution only if the sparsity is at least 15%

        totalWeights = np.sum(x)

        indices = x>1.e-7*totalWeights

        if len(indices) > 0.15*len(integrationWeights):

            return np.array([]), np.array([])

        else:# pragma: no cover

            return  np.where(indices)[0], x[indices]

    else:# pragma: no cover
        # return an empty solution

        return  np.array([]), np.array([])



def CallOptimizer(c, A_ub, b_ub, method, options):


    from scipy.optimize import linprog as lp

    return lp(c = c, A_ub = A_ub, b_ub = b_ub, method = method,\
              options = options)


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)