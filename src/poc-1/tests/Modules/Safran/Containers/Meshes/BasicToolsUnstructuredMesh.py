# -*- coding: utf-8 -*-

from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM


def test():

    mesh = BTUM.BasicToolsUnstructuredMesh(
        CreateCube(dimensions=[3, 4, 3], spacing=[2.0, 2.0, 2.0], ofTetras=True)
    )

    mesh.GetNodes()
    for el in mesh.AllElementsIterator():
        True

    print(mesh)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
