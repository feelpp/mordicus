# -*- coding: utf-8 -*-
import os
import numpy as np
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.Containers import Solution
from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
import collections

def test():

    mesh = BTUM.BasicToolsUnstructuredMesh(
        CreateCube(dimensions=[3, 4, 3], spacing=[2.0, 2.0, 2.0], ofTetras=True)
    )

    solution = Solution.Solution("test", 1, mesh.GetNumberOfNodes(), True)

    modes = np.ones((3, mesh.GetNumberOfNodes()))
    compressedSnapshots = collections.OrderedDict()
    for t in range(7):
        compressedSnapshots[float(t)] = np.ones(3)

    solution.SetCompressedSnapshots(compressedSnapshots)

    PW.WritePXDMF(mesh, compressedSnapshots, modes, "test")
    PW.WritePXDMFFromSolution(mesh, solution, modes)
    PW.WriteReducedOrderBasisToPXDMF(mesh, modes, "test")

    os.system("rm -rf test0.bin test.pxdmf")
    os.system("rm -rf ReducedOrderBasis_test0.bin ReducedOrderBasis_test.pxdmf")

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
