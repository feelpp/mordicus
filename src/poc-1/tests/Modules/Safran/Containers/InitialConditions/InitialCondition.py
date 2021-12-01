# -*- coding: utf-8 -*-

import numpy as np
from Mordicus.Modules.Safran.Containers.InitialConditions import InitialCondition as IC


def test():

    initialCondition = IC.InitialCondition()

    print(initialCondition)

    reducedOrderBases = {"U":np.random.rand(2,3)}

    initialCondition.SetDataType("U", "scalar")
    initialCondition.GetDataType("U")
    initialCondition.SetInitialSnapshot("U", 0.)
    initialCondition.SetReducedInitialSnapshot("U", np.zeros(2))
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)
    initialCondition.GetReducedInitialSnapshot("U")
    snapshotCorrelationOperator = {"U":np.eye(3)}

    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)

    initialCondition.SetInitialSnapshot("U", 1.)
    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)


    initialCondition.SetDataType("U", "vector")
    initialCondition.SetInitialSnapshot("U", np.ones(3))
    initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)
    initialCondition.ReduceInitialSnapshot(reducedOrderBases)

    initialCondition.__getstate__()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
