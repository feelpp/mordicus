# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.IO import SolutionReaderBase as SRB


def test():

    solutionReaderBase = SRB.SolutionReaderBase()
    print(solutionReaderBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
