# -*- coding: utf-8 -*-

from Mordicus.Core.IO import InputReaderBase as IRB


def test():

    inputReaderBase = IRB.InputReaderBase()
    print(inputReaderBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
