# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.FixedData import FixedDataBase as FDB


def test():


    fixedData = FDB.FixedDataBase()

    fixedData.SetInternalStorage("toto")
    assert fixedData.GetInternalStorage() == "toto"

    print(fixedData)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
