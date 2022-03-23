# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.FieldHandlers import FieldHandlerBase as FHB


def test():


    fieldHandler = FHB.FieldHandlerBase()

    fieldHandler.SetInternalStorage("toto")
    assert fieldHandler.GetInternalStorage() == "toto"

    print(fieldHandler)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
