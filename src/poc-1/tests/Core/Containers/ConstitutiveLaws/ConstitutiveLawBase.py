# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ConstitutiveLaws import ConstitutiveLawBase as CLB


def test():

    constitutiveLaw = CLB.ConstitutiveLawBase("set1", "type1")

    assert constitutiveLaw.GetSet() == "set1"
    assert constitutiveLaw.GetType() == "type1"
    assert constitutiveLaw.GetIdentifier() == ("type1","set1")

    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
