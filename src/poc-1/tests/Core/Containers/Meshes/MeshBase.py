# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

from Mordicus.Core.Containers.Meshes import MeshBase as MB


def test():
    meshBase = MB.MeshBase()
    meshBase.SetInternalStorage(1)
    meshBase.SetInternalStorage(1)
    assert meshBase.GetInternalStorage() == 1
    assert meshBase.GetNumberOfNodes() == 0
    assert meshBase.GetDimensionality() == 0

    print(meshBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
