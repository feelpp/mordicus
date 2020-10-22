# -*- coding: utf-8 -*-

import numpy as np
from Mordicus.Modules.Safran.Containers.InitialConditions import InitialCondition as IC


def test():

    initialCondition = IC.InitialCondition()

    print(initialCondition)

    initialCondition.SetDataType("scalar")
    initialCondition.GetDataType()
    initialCondition.SetInitialSnapshot(0.)
    initialCondition.SetReducedInitialSnapshot(np.zeros(2))
    initialCondition.GetReducedInitialSnapshot()
    initialCondition.ReduceInitialSnapshot(np.random.rand(2,3), np.eye(3))

    initialCondition.SetInitialSnapshot(1.)
    initialCondition.ReduceInitialSnapshot(np.random.rand(2,3), np.eye(3))

    initialCondition.__getstate__()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
