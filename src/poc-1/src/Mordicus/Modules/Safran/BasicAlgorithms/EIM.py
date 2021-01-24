# -*- coding: utf-8 -*-
import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1:# pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import scipy.linalg as sla


def QDEIM(basis):
    """
    Generate empirical sample entries using the Q-DEIM algorithm [1].

    Parameters
    ----------
    basis : array-like
        An orthonormal multivector.

    Returns
    -------
    ndarray of ints
        An 1-d array containing the sample entries.

    Notes
    -----
        A multivector is an (n, N)-array where n is the number of vectors and N
        the numbers of dofs.

    References
    ----------
        [1] Z. Drmac and S. Gugercin. A New Selection Operator for the Discrete
        Empirical Interpolation Method : Improved a priori error bound and
        extensions, 2015. URL: http://arxiv.org/abs/1505.00370.
    """

    Q, R, P = sla.qr(basis, pivoting=True)
    return P[:basis.shape[0]]


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)