# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.FixedData import FixedDataBase as FDB


def test():


    fixedData = FDB.FixedDataBase()

    fixedData.SetInternalStorage("toto")
    assert fixedData.GetInternalStorage() == "toto"

    print(fixedData)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
