# -*- coding: utf-8 -*-

import numpy as np
from Mordicus.Modules.Safran.Containers.InitialConditions import InitialCondition as IC


def test():

    initialCondition = IC.InitialCondition()

    print(initialCondition)

    initialCondition.SetDataType("U", "scalar")
    initialCondition.GetDataType("U")
    initialCondition.SetInitialSnapshot("U", 0.)
    initialCondition.SetReducedInitialSnapshot("U", np.zeros(2))
    initialCondition.GetReducedInitialSnapshot("U")
    reducedOrderBases = {"U":np.random.rand(2,3)}
    snapshotCorrelationOperator = {"U":np.eye(3)}
    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)

    initialCondition.SetInitialSnapshot("U", 1.)
    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)

    initialCondition.__getstate__()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
