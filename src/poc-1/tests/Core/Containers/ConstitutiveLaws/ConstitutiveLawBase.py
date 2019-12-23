# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ConstitutiveLaws import ConstitutiveLawBase as CLB


def test():

    constitutiveLaw = CLB.ConstitutiveLawBase("set1", "type1")
    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()
    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
