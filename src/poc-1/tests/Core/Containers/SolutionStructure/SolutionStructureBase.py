# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.SolutionStructures import SolutionStructureBase as SSB

from Mordicus.Core.Containers.Meshes import MeshBase as MB


def test():

    meshBase = MB.MeshBase()
    solutionStructure = SSB.SolutionStructureBase(meshBase, 'node')

    solutionStructure.SetInternalStorage("storage")
    solutionStructure.SetInternalStorage("storage")
    assert solutionStructure.GetInternalStorage() == "storage"



if __name__ == "__main__":
    print(test())  # pragma: no cover


