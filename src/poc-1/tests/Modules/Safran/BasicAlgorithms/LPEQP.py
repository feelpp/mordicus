# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import LPEQP


def test():


    tolerance = 1.e-1

    integrationWeights = np.array([0.01607169, 0.70413293, 0.31361787, 0.1364099,  0.7917212,  0.08945926,\
                          0.9075343,  0.33644464, 0.65143926, 0.59733275])

    integrands = np.array([[0.92628366, 0.51742321, 0.9061643,  0.27057508, 0.37272805, 0.9422968,\
                   0.76672656, 0.33835427, 0.34265795, 0.79223508],
                  [0.90569203, 0.89534547, 0.40520877, 0.49520074, 0.55787095, 0.65994347,\
                   0.05542419, 0.04961487, 0.35419613, 0.0268553 ]])

    integrals = np.dot(integrands, integrationWeights)
    normIntegrals = np.linalg.norm(integrals)

    reducedIntegrationPoints, reducedIntegrationWeights = LPEQP.LPEQP(integrationWeights,\
                      integrands, integrals, normIntegrals, tolerance)



    np.testing.assert_almost_equal(reducedIntegrationPoints, [5])
    np.testing.assert_almost_equal(reducedIntegrationWeights, [2.41841848])

    integrationWeights = np.ones(10)
    integrands = np.ones(20).reshape((2,10))
    integrals = np.dot(integrands, integrationWeights)
    normIntegrals = np.linalg.norm(integrals)

    reducedIntegrationPoints, reducedIntegrationWeights = LPEQP.LPEQP(integrationWeights,\
                      integrands, integrals, normIntegrals, tolerance)

    np.testing.assert_almost_equal(reducedIntegrationPoints, [])
    np.testing.assert_almost_equal(reducedIntegrationWeights, [])

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


