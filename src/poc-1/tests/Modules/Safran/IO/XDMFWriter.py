# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import os
import numpy as np
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from Mordicus.Modules.Safran.IO import XDMFWriter as XW
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import ProblemData
from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
from Mordicus.Core.Helpers import FolderHandler as FH
import filecmp


def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()

    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3, 4, 3], spacing=[2.0, 2.0, 2.0], ofTetras=True))

    numberOfElements = mesh.GetInternalStorage().elements['tet4'].GetNumberOfElements()
    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

    solutionU = Solution.Solution("U", 3, numberOfNodes, True)
    solutionT = Solution.Solution("T", 1, numberOfNodes, True)
    solutionP = Solution.Solution("P", 1, numberOfIntegrationPoints, False)

    problemData = ProblemData.ProblemData("test")
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionT)
    problemData.AddSolution(solutionP)

    snapshotsU = {}
    snapshotsT = {}
    snapshotsP = {}
    for t in range(7):
        snapshotsU[float(t)] = t*np.ones(numberOfNodes*3)
        snapshotsT[float(t)] = 2.*t*np.ones(numberOfNodes)
        snapshotsP[float(t)] = 3.*(t+1)*np.ones(numberOfElements)

    solutionU.SetSnapshots(snapshotsU)
    solutionT.SetSnapshots(snapshotsT)
    solutionP.SetSnapshots(snapshotsP)

    XW.WriteSolution(mesh, solutionU, 'XDMFWriter1')
    XW.WriteSolution(mesh, solutionP, 'XDMFWriter2')
    XW.WriteProblemDataSolutions(mesh, problemData, 'U', 'XDMFWriter3')

    reducedOrderBasisU = np.arange(3*3*numberOfNodes).reshape(3,-1)
    reducedOrderBasisT = np.arange(3*numberOfNodes).reshape(3,-1)
    reducedOrderBasisP = np.arange(2*numberOfIntegrationPoints).reshape(2,-1)
    reducedOrderBases = {"U":reducedOrderBasisU, "T":reducedOrderBasisT, "P":reducedOrderBasisP}

    problemData.CompressSolution("U", reducedOrderBasisU)
    problemData.CompressSolution("T", reducedOrderBasisT)
    problemData.CompressSolution("P", reducedOrderBasisP)

    XW.WriteReducedOrderBases(mesh, problemData, reducedOrderBases, 'XDMFWriter4')

    #comparison deactivated: the order of data in file dependends on the folder from which the script is run...
    """
    assert filecmp.cmp('XDMFWriter1.xmf', 'ref/XDMFWriter1.xmf', shallow=False) == True
    assert filecmp.cmp('XDMFWriter10.bin',  'ref/XDMFWriter10.bin', shallow=False) == True
    assert filecmp.cmp('XDMFWriter2.xmf', 'ref/XDMFWriter2.xmf', shallow=False) == True
    assert filecmp.cmp('XDMFWriter20.bin',  'ref/XDMFWriter20.bin', shallow=False) == True
    assert filecmp.cmp('XDMFWriter3.xmf', 'ref/XDMFWriter3.xmf', shallow=False) == True
    assert filecmp.cmp('XDMFWriter30.bin',  'ref/XDMFWriter30.bin', shallow=False) == True
    assert filecmp.cmp('XDMFWriter4.xmf', 'ref/XDMFWriter4.xmf', shallow=False) == True
    assert filecmp.cmp('XDMFWriter40.bin',  'ref/XDMFWriter40.bin', shallow=False) == True
    """

    os.system("rm -rf XDMFWriter10.bin XDMFWriter1.xmf")
    os.system("rm -rf XDMFWriter20.bin XDMFWriter2.xmf")
    os.system("rm -rf XDMFWriter30.bin XDMFWriter3.xmf")
    os.system("rm -rf XDMFWriter40.bin XDMFWriter4.xmf")


    folderHandler.SwitchToExecutionFolder()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
