# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath


def test():

    folder = GetTestDataPath() + "Zset/MecaSequential/"

    meshFileName = folder + "cube.geof"

    reader = ZMR.ZsetMeshReader(meshFileName)
    reader.ReadMesh()

    ZMR.ReadMesh(meshFileName)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
