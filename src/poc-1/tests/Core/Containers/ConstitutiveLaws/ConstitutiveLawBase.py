# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


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
