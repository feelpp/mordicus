# -*- coding: utf-8 -*-
from MordicusCore.Containers.Meshes import MeshBase as MB



def test():
    meshBase = MB.MeshBase()
    meshBase.GetNumberOfNodes()
    meshBase.GetDimensionality()
    print(meshBase)
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
