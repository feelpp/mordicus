# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings import LoadingBase as LB


def test():

    loading = LB.LoadingBase("solutionName", "set1", "type1")
    loading.GetSet()
    loading.GetType()
    loading.GetIdentifier()
    loading.GetSolutionName()
    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
