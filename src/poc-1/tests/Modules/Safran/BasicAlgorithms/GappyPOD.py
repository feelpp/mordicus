# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP


def test():

    ModesAtMask = np.array([[1., 0., 0.], [0., 1., 0.]])
    fieldAtMask = np.array([1., 0., 1.])
    GP.Fit(ModesAtMask, fieldAtMask)
    GP.FitAndCost(ModesAtMask, fieldAtMask)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
