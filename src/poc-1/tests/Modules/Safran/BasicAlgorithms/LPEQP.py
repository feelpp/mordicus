# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import LPEQP


def test():

    integrationWeights = np.arange(20)
    integrands = np.random.rand(10,20)
    integrals = np.dot(integrands, integrationWeights)
    normIntegrals = np.linalg.norm(integrals)

    tolerance = 1.e-6

    LPEQP.LPEQP(integrationWeights, integrands, integrals,\
                normIntegrals, tolerance)


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


