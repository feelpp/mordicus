# -*- coding: utf-8 -*-

from MordicusCore.Containers.Loadings import LoadingBase as LB


def test():

    loading = LB.LoadingBase()
    loading.SetSet("toto")
    loading.GetSet()
    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
