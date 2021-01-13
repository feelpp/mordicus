# -*- coding: utf-8 -*-
import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: 
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"

from scipy.optimize import lsq_linear as lsq_linear


def Fit(ModesAtMask, fieldAtMask):
    """
    Fits GappyPOD approximation

    ModesAtMask: nbeModes, maskSize
    fieldAtMask: maskSize
    """
    lstqr = lsq_linear(ModesAtMask.T, fieldAtMask)

    return lstqr['x']


def FitAndCost(ModesAtMask, fieldAtMask):
    """
    Fits GappyPOD approximation an return prediction and cost

    ModesAtMask: nbeModes, maskSize
    fieldAtMask: maskSize
    """
    lstqr = lsq_linear(ModesAtMask.T, fieldAtMask)

    return lstqr['x'], lstqr['cost']


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)