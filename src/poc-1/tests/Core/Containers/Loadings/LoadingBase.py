# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.Loadings import LoadingBase as LB


def test():

    loading = LB.LoadingBase("solutionName", "set1", "type1")

    assert loading.GetSet() == "set1"
    assert loading.GetType() == "type1"
    assert loading.GetSolutionName() == "solutionName"
    assert loading.GetIdentifier() == ("solutionName","type1","set1")


    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
