# -*- coding: utf-8 -*-


from MordicusModules.safran.IO import ZsetReader as ZR
from MordicusCore import GetTestDataPath

def test():


    folder = GetTestDataPath()+"Zset/"
    
    inputFileName = folder + "cube.inp"
    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"
    
    reader = ZR.ZsetReader(inputFileName, meshFileName, solutionFileName)
    
    inputTimeSequence = reader.ReadInputTimeSequence()
    inputTimeSequence = ZR.ReadInputTimeSequence(inputFileName)
    
    snapshot = reader.ReadSnapshot("U1", inputTimeSequence[0], primality = True)
    snapshot = ZR.ReadSnapshot(solutionFileName, "U1", inputTimeSequence[0], primality = True)

    mesh = reader.ReadMesh()
    mesh = ZR.ReadMesh(meshFileName)

    outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()
    outputTimeSequence = ZR.ReadTimeSequenceFromSolutionFile(solutionFileName)

    loadings = reader.ConstructLoadingsList()
    loadings = ZR.ConstructLoadingsList(inputFileName)
    
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
