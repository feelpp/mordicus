# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
from Mordicus.Modules.Safran.Containers.InitialConditions import InitialCondition as IC


def test():

    initialCondition = IC.InitialCondition()

    reducedOrderBases = {"U":np.array(np.arange(30).reshape(3,10), dtype=float)}

    initialCondition.SetDataType("U", "scalar")
    assert initialCondition.GetDataType("U") == "scalar"
    initialCondition.SetInitialSnapshot("U", 0.)
    initialCondition.SetReducedInitialSnapshot("U", np.zeros(3))
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [0., 0., 0.])
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [0., 0., 0.])
    snapshotCorrelationOperator = {"U":2.*np.eye(10)}

    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [0., 0., 0.])
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [0., 0., 0.])

    initialCondition.SetInitialSnapshot("U", 1.)
    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [90., 290., 490.])
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [45., 145., 245.])


    initialCondition.SetDataType("U", "vector")
    assert initialCondition.GetDataType("U") == "vector"
    initialCondition.SetInitialSnapshot("U", np.array(np.arange(10), dtype=float))
    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [570., 1470., 2370.])
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)
    np.testing.assert_almost_equal(initialCondition.GetReducedInitialSnapshot("U"), [285.,  735., 1185.])

    initialCondition.__getstate__()

    print(initialCondition)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
