# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath
import numpy as np

def test():

    folder = GetTestDataPath() + "Zset/MecaSequential/"

    meshFileName = folder + "cube.geof"

    reader = ZMR.ZsetMeshReader(meshFileName)
    mesh = reader.ReadMesh()

    np.testing.assert_almost_equal(mesh.GetInternalStorage().nodes[0], [0.,0.,0.])
    np.testing.assert_almost_equal(mesh.GetInternalStorage().nodes[150], [0.5,0.,0.5])
    np.testing.assert_almost_equal(mesh.GetInternalStorage().nodes[-1], [1.,1.,1.])
    assert len(mesh.GetInternalStorage().GetElementsOfType('hex8').GetTag('ELAS')) == 108
    assert mesh.GetNumberOfNodes() == 343

    ZMR.ReadMesh(meshFileName)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
