# -*- coding: utf-8 -*-
from MordicusCore.Containers.BaseObject import BaseObject
from MordicusCore.Containers.CompressedFormats import CompressedFormatsBase as CFB
        

def test():

    compressedFormatsBase = CFB.CompressedFormatsBase("toto")
    compressedFormatsBase.GetName()
    print(compressedFormatsBase)
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
