# -*- coding: utf-8 -*-
from Mordicus.Core.Containers.Meshes import MeshBase as MB


def test():
    meshBase = MB.MeshBase()
    meshBase.SetInternalStorage(1)
    meshBase.SetInternalStorage(1)
    meshBase.GetInternalStorage()
    meshBase.GetNumberOfNodes()
    meshBase.GetDimensionality()
    print(meshBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
