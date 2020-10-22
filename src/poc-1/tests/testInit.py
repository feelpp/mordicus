# -*- coding: utf-8 -*-

from Mordicus import GetTestDataPath, GetTestPath


def test():

    print("tests path is :", GetTestPath())
    print("TestsData path is :", GetTestDataPath())
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
