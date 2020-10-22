# -*- coding: utf-8 -*-

from Mordicus.Core.IO import SolutionReaderBase as SRB


def test():

    solutionReaderBase = SRB.SolutionReaderBase()
    print(solutionReaderBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
