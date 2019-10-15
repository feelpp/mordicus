# -*- coding: utf-8 -*-

import openturns as ot
from Mordicus.Modules.Phimeca.IO.OTMeshReader import OTMeshReader


def test():

    # create a regular 2-d mesh defined on an interval
    ot_mesh = ot.IntervalMesher([10, 5]).build(ot.Interval([0.0, 0.0], [2.0, 1.0]))

    reader = OTMeshReader(ot_mesh)
    mesh = reader.ReadMesh()
    assert mesh.GetNumberOfNodes() == 11 * 6, "wrong node number"
    assert mesh.GetDimensionality() == 2, "wrong dimension"
    for el in mesh.AllElementsIterator():
        pass
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
