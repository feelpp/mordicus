# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.OperatorCompressors import ReducedQuadratureProcedure as RQP



def test():

    integrationWeights = np.arange(20)
    integrands = np.arange(200).reshape(10, 20)
    reducedIntegrationPointsInitSet = []
    imposedIndices = [1, 2]

    tolerance = 1.e-6

    res = RQP.ComputeReducedIntegrationScheme(integrationWeights, integrands,\
        tolerance, nRandom = 0)

    np.testing.assert_almost_equal(res[0], [19, 0])
    np.testing.assert_almost_equal(res[1], [130., 60.])


    res = RQP.ComputeReducedIntegrationScheme(integrationWeights, integrands,\
        tolerance, imposedIndices, reducedIntegrationPointsInitSet, nRandom = 0)

    np.testing.assert_almost_equal(res[0], [19, 0, 1, 2])
    np.testing.assert_almost_equal(res[1], [130., 60., 0., 0.])

    reducedIntegrationPointsInitSet = [3, 4]


    res = RQP.ComputeReducedIntegrationScheme(integrationWeights, integrands,\
        tolerance, imposedIndices, reducedIntegrationPointsInitSet, nRandom = 0)

    np.testing.assert_almost_equal(res[0], [3, 4, 19, 1, 2])
    np.testing.assert_almost_equal(res[1], [34.29460581,39.41908714,116.28630705,0.,0.])


    res = RQP.ComputeReducedIntegrationScheme(integrationWeights, integrands,\
        tolerance, imposedIndices, reducedIntegrationPointsInitSet,\
        initByLPEQP = True, nRandom = 0)

    np.testing.assert_almost_equal(res[0], [19,  0,  1,  2])
    np.testing.assert_almost_equal(res[1], [130., 60., 0., 0.])


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
