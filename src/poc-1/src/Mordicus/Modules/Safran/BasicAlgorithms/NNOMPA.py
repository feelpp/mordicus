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

from BasicTools.Helpers.TextFormatHelper import TFormat



def NNOMPA(integrationWeights, integrands, integrals, normIntegrals, tolerance,\
          reducedIntegrationPointsInitSet, maxIter = 10000, nRandom = 1):
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
    normIntegrals : float
        np.linalg.norm(integrals), already computed in mordicus use
    tolerance : float
        upper bound for the accuracy of the reduced integration scheme on the
        provided integrands
    reducedIntegrationPointsInitSet : np.ndarray
        of size (numberOfInitReducedIntegratonPoints,), dtype = int.
        Initial guess for the indices of the reducedIntegrationScheme (can be
        empty)
    maxIter : int, optional
        Maximum iteration for the matching pursuit algorithm
    nRandom : int, optional
        number of random points added at each iteration

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


    while err > tolerance and count0 < maxIter:

        #nRandom = numberOfIntegrationPointsToSelect - len(s)
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


            optimRes = CallOptimizer(integrands_s, integrals, max_iter = None)


            xTemp = optimRes['x']

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
            " sample(s) to decrease interpolation error)")); sys.stdout.flush()


    return s, x




def CallOptimizer(integrands_s, integrals, max_iter = None):

    """
    Exemple of scipy optimizer wrapper (here lsq_linear)

    Parameters
    ----------
    A : array_like, sparse matrix of LinearOperator, shape (m, n)
        Design matrix. Can be `scipy.sparse.linalg.LinearOperator`.
    b : array_like, shape (m,)
        Target vector.
    max_iter : None or int, optional
        Maximum number of iterations before termination. If None (default), it
        is set to the number of variables for ``method='bvls'``.

    Returns
    -------
    res : OptimizeResult
        see the class `scipy.optimize.OptimizeResult`
    """
    #from scipy.optimize import nnls as nnls
    #optimRes = {}
    #optimRes['x'] = nnls(integrands_s, integrals, maxiter=max_iter)[0]


    from scipy.optimize import lsq_linear as lsq_linear
    optimRes = lsq_linear(integrands_s, integrals, bounds=(0.,np.inf), method=\
                      'bvls', lsmr_tol='auto', verbose = 0, \
                      lsq_solver='exact', max_iter = max_iter, tol = 1e-8)

    return optimRes



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
