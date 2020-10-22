# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import EIM


def test():

    basis = np.array([[1., 0.], [0., 1.]])

    EIM.QDEIM(basis)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
