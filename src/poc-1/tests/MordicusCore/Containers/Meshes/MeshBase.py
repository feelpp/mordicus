# -*- coding: utf-8 -*-
from MordicusCore.Containers.Meshes import MeshBase as MB



def test():
    # GetNumberOfNodes and GetDimensionality not tested here
    meshBase = MB.MeshBase()
    print(meshBase)
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
