# -*- coding: utf-8 -*-

from Mordicus.Core import GetTestDataPath, GetTestPath


def test():

    GetTestDataPath()
    GetTestPath()
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
