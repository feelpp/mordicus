# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.IO import ReaderBase as RB

def test():

    readerBase = RB.ReaderBase()
    print(readerBase)
    return "ok"



if __name__ == '__main__':
    print(test()) #pragma: no cover
