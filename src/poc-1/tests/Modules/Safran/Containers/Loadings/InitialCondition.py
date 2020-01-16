# -*- coding: utf-8 -*-

import numpy as np
import collections
from Mordicus.Modules.Safran.Containers.Loadings import InitialCondition as IC


def test():


    loading = IC.InitialCondition("set1")
    loading.SetType("vector")
    loading.__getstate__()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
