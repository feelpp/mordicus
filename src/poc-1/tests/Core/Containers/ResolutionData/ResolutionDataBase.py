# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ResolutionData import ResolutionDataBase as RDB


def test():

    resolutionDataBase = RDB.ResolutionDataBase()

    resolutionDataBase.SetInternalStorage("storage")
    resolutionDataBase.SetInternalStorage("storage")
    assert resolutionDataBase.GetInternalStorage() == "storage"



if __name__ == "__main__":
    print(test())  # pragma: no cover
