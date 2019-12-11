# -*- coding: utf-8 -*-
import os

from MordicusCore.Containers import BaseObject as BO


def test():

    baseObject = BO.BaseObject()
    baseObject.SetInternalStorage("toto")
    baseObject.GetInternalStorage()

    baseObject.Save("test")
    os.system("rm -rf test.pkl")

    print(baseObject)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
