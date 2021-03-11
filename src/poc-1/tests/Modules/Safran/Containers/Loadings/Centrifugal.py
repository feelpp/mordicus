# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.Loadings import Centrifugal as C


def test():

    loading = C.Centrifugal("U", "set1")
    
    loading.__getstate__()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
