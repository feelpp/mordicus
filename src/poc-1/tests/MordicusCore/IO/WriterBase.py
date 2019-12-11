# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.IO import WriterBase as WB


def test():

    writerBase = WB.WriterBase()
    print(writerBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
