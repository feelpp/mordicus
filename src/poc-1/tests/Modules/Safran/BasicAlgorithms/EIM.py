# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import EIM


def test():

    basis = np.array([[1., 0.], [0., 1.]])

    np.testing.assert_almost_equal(EIM.QDEIM(basis), [0., 1.])


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
