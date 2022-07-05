# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA


def test():

    integrationWeights = np.arange(20)
    integrands = np.arange(200).reshape((10,20))
    integrals = np.dot(integrands, integrationWeights)
    normIntegrals = np.linalg.norm(integrals)
    reducedIntegrationPointsInitSet = []

    tolerance = 1.e-6

    reducedIntegrationPoints, reducedIntegrationWeights = NNOMPA.NNOMPA(integrationWeights, integrands, integrals,\
                  normIntegrals, tolerance, reducedIntegrationPointsInitSet, nRandom = 0)

    np.testing.assert_almost_equal(reducedIntegrationPoints, [19,  0])
    np.testing.assert_almost_equal(reducedIntegrationWeights, [130.,  60.])

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


