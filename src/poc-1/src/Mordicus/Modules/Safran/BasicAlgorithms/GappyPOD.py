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

from scipy.optimize import lsq_linear as lsq_linear


def Fit(modesAtMask, fieldAtMask):
    """
    Fits GappyPOD approximation

    Parameters
    ----------
    modesAtMask:
        np.ndarray of size (nbeModes, maskSize)
    fieldAtMask: np.ndarray
        np.ndarray of size (maskSize,)

    Returns
    -------
    np.ndarray
        of size (nbeModes,)
    """
    lstqr = lsq_linear(modesAtMask.T, fieldAtMask)

    return lstqr['x']


def FitAndCost(modesAtMask, fieldAtMask):
    """
    Fits GappyPOD approximation an return prediction and cost

    Parameters
    ----------
    modesAtMask:
        np.ndarray of size (nbeModes, maskSize)
    fieldAtMask: np.ndarray
        np.ndarray of size (maskSize,)

    Returns
    -------
    np.ndarray
        of size (nbeModes,)
    float
        evaluation of the cost function at convergence
    """
    lstqr = lsq_linear(modesAtMask.T, fieldAtMask)

    normFieldAtMask = np.linalg.norm(fieldAtMask)
    if normFieldAtMask > 1.e-10:
        cost = lstqr['cost']/np.linalg.norm(fieldAtMask)
    else:# pragma: no cover
        cost = lstqr['cost']

    return lstqr['x'], cost


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)