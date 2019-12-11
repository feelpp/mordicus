# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.IO import SolutionReaderBase as SRB


def test():

    solutionReaderBase = SRB.SolutionReaderBase()
    print(solutionReaderBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
