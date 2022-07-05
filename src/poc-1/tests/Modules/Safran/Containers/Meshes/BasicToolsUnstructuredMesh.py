# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
import numpy as np

def test():

    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[2, 2, 2], spacing=[1.0, 2.0, 3.0], ofTetras=True))

    np.testing.assert_almost_equal(mesh.GetNodes(), np.array([[-1., -1., -1.],
     [-1., -1.,  2.],
     [-1.,  1., -1.],
     [-1.,  1.,  2.],
     [ 0., -1., -1.],
     [ 0., -1.,  2.],
     [ 0.,  1., -1.],
     [ 0.,  1.,  2.]]))

    for el in mesh.AllElementsIterator():
        True

    print(mesh)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
