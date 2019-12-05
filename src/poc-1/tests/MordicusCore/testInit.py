# -*- coding: utf-8 -*-

from MordicusCore import GetTestDataPath


def test():

    GetTestDataPath()
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover

