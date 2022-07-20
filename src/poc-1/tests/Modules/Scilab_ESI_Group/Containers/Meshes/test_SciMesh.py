# -*- coding: utf-8 -*-

from Mordicus.Modules.Scilab_ESI_Group.IO.SciMeshReader import SciMeshReader

from pathlib import Path
import os


def test():

    testFilePath = os.path.join(os.path.dirname(__file__), "..", "..", "data", "Mesh")

    #import mesh from path
    reader2 = SciMeshReader(testFilePath)

    # get mesh
    mesh = reader2.ReadMesh()

    # tests

    #nodes
    assert mesh.GetNumberOfNodes() == 10906, "Wrong number of nodes"
    #dims
    assert mesh.GetDimensionality() == 2, "Wrong dimensionality"
    # iterator
    for el in mesh.AllElementsIterator():
        pass

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
