# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.FieldHandlers import FieldHandlerBase as FHB


def test():


    fieldHandler = FHB.FieldHandlerBase()

    fieldHandler.SetInternalStorage("toto")
    assert fieldHandler.GetInternalStorage() == "toto"

    print(fieldHandler)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
