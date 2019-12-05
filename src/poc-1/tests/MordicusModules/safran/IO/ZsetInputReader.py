# -*- coding: utf-8 -*-


from MordicusModules.safran.IO import ZsetInputReader as ZIR
from MordicusCore import GetTestDataPath

def test():


    folder = GetTestDataPath()+"Zset/"
    
    inputFileName = folder + "cube.inp"
    
    reader = ZIR.ZsetInputReader(inputFileName)
    
    inputTimeSequence = reader.ReadInputTimeSequence()
    inputTimeSequence = ZIR.ReadInputTimeSequence(inputFileName)

    loadings = reader.ConstructLoadingsList()
    loadings = ZIR.ConstructLoadingsList(inputFileName)
    
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
