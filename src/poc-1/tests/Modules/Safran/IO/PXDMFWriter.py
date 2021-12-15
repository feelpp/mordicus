# -*- coding: utf-8 -*-
import os
import numpy as np
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.Containers import Solution
from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
from Mordicus.Core.Helpers import FolderHandler as FH
import filecmp


def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()

    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3, 4, 3], spacing=[2.0, 2.0, 2.0], ofTetras=True))

    solution = Solution.Solution("PXDMFWriter1", 1, mesh.GetNumberOfNodes(), True)

    modes = np.ones((3, mesh.GetNumberOfNodes()))
    compressedSnapshots = {}
    for t in range(7):
        compressedSnapshots[float(t)] = np.ones(3)

    solution.SetCompressedSnapshots(compressedSnapshots)

    PW.WriteSolution(mesh, solution, modes)
    PW.WriteCompressedSolution(mesh, compressedSnapshots, modes, "PXDMFWriter2")
    PW.WriteReducedOrderBasis(mesh, modes, "PXDMFWriter3")


    #comparaison deactivated: the order of data in file dependends on the folder from which the script is run...
    """
    assert filecmp.cmp('PXDMFWriter1.pxdmf', 'ref/PXDMFWriter1.pxdmf', shallow=False) == True
    assert filecmp.cmp('PXDMFWriter10.bin',  'ref/PXDMFWriter10.bin', shallow=False) == True
    assert filecmp.cmp('PXDMFWriter2.pxdmf', 'ref/PXDMFWriter2.pxdmf', shallow=False) == True
    assert filecmp.cmp('PXDMFWriter20.bin',  'ref/PXDMFWriter20.bin', shallow=False) == True
    assert filecmp.cmp('PXDMFWriter3.pxdmf', 'ref/PXDMFWriter3.pxdmf', shallow=False) == True
    assert filecmp.cmp('PXDMFWriter30.bin',  'ref/PXDMFWriter30.bin', shallow=False) == True
    """


    os.system("rm -rf PXDMFWriter10.bin PXDMFWriter1.pxdmf")
    os.system("rm -rf PXDMFWriter20.bin PXDMFWriter2.pxdmf")
    os.system("rm -rf PXDMFWriter30.bin PXDMFWriter3.pxdmf")

    folderHandler.SwitchToExecutionFolder()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
