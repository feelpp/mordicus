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


def TruncatedSVDSymLower(matrix, epsilon):
    """
    Computes a truncatd singular value decomposition of a symetric definite
    matrix in scipy.sparse.csr format. Only the lower triangular part needs
    to be defined

    Parameters
    ----------
    matrix : scipy.sparse.csr
        the input matrix
    epsilon : float
        the truncation tolerence, determining the number of keps eigenvalues

    Returns
    -------
    np.ndarray
        kept eigenvalues, of size (numberOfEigenvalues)
    np.ndarray
        kept eigenvectors, of size (numberOfEigenvalues, numberOfSnapshots)
    """

    eigenValues, eigenVectors = np.linalg.eigh(matrix, UPLO="L")

    idx = eigenValues.argsort()[::-1]
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:, idx]

    id_max = 0
    bound = (epsilon ** 2) * eigenValues[0]
    for e in eigenValues:
        if e > bound:
            id_max += 1
    id_max2 = 0
    bound = (1 - epsilon ** 2) * np.sum(eigenValues)
    temp = 0
    for e in eigenValues:
        temp += e
        if temp < bound:
            id_max2 += 1  # pragma: no cover

    id_max = max(id_max, id_max2)

    return eigenValues[0:id_max], eigenVectors[:, 0:id_max]


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

