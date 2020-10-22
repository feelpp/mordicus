 # -*- coding: utf-8 -*-

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