# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings import LoadingBase as LB


def test():

    loading = LB.LoadingBase("set1", "type1")
    loading.GetSet()
    loading.GetType()
    loading.GetIdentifier()
    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
