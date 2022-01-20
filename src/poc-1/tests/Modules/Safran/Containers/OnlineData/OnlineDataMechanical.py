# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.OnlineData import OnlineDataMechanical as ODM


def test():

    onlineDataMechanical = ODM.OnlineDataMechanical(1, 1)

    print(onlineDataMechanical)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
