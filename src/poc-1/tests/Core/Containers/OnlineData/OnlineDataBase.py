# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OnlineData import OnlineDataBase as ODB


def test():

    onlineDataBase = ODB.OnlineDataBase("U")

    assert onlineDataBase.GetSolutionName() == "U"

    print(onlineDataBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover