# -*- coding: utf-8 -*-


from MordicusModules.safran.IO import ZsetMeshReader as ZMR
from MordicusCore import GetTestDataPath

def test():


    folder = GetTestDataPath()+"Zset/"
    
    meshFileName = folder + "cube.geof"
    
    reader = ZMR.ZsetMeshReader(meshFileName)
    
    mesh = reader.ReadMesh()
    mesh = ZMR.ReadMesh(meshFileName)

    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
