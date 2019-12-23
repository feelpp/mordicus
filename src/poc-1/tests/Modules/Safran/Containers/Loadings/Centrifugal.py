# -*- coding: utf-8 -*-

import numpy as np
import collections
from Mordicus.Modules.Safran.Containers.Loadings import Centrifugal as C


def test():

    loading = C.Centrifugal("set1")
    loading.DeleteHeavyData()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
