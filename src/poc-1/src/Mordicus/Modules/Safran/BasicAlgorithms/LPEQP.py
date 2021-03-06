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

        reducedIntegrationPoints, reducedIntegrationWeights = np.where(indices)[0], x[indices]

        if len(reducedIntegrationPoints) > 0.15*len(integrationWeights):
            print(str(100*len(reducedIntegrationPoints)/len(integrationWeights))+"% of nonzero integration weights")
            return  np.array([]), np.array([])
        else:
            return  reducedIntegrationPoints, reducedIntegrationWeights


    else:# pragma: no cover
        # return an empty solution

        return  np.array([]), np.array([])



def CallOptimizer(c, A_ub, b_ub, method, options):
    """
    Exemple of scipy optimizer wrapper (here linprog)

    Parameters
    ----------
    c : 1-D array
        The coefficients of the linear objective function to be minimized.
    A_ub : 2-D array
        The inequality constraint matrix. Each row of ``A_ub`` specifies the
        coefficients of a linear inequality constraint on ``x``.
    b_ub : 1-D array
        The inequality constraint vector. Each element represents an
        upper bound on the corresponding value of ``A_ub @ x``.
    method : str, optional
        The algorithm used to solve the standard form problem.
    options : dict, optional
        A dictionary of solver options.

    Returns
    -------
    res : OptimizeResult
        see the class `scipy.optimize.OptimizeResult`
    """
    from scipy.optimize import linprog as lp

    return lp(c = c, A_ub = A_ub, b_ub = b_ub, method = method,\
              options = options)


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)