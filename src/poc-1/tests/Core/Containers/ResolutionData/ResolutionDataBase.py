# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.ResolutionData import ResolutionDataBase as RDB


def test():

    resolutionDataBase = RDB.ResolutionDataBase()

    resolutionDataBase.SetInternalStorage("storage")
    resolutionDataBase.SetInternalStorage("storage")
    assert resolutionDataBase.GetInternalStorage() == "storage"



if __name__ == "__main__":
    print(test())  # pragma: no cover
