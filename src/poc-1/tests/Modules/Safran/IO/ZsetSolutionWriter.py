# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
import os
from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Modules.Safran.IO import ZsetSolutionWriter as ZSW
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.FE import FETools as FE
from Mordicus import GetTestDataPath, GetTestPath
import filecmp

def test():

    meshFileName = GetTestDataPath() + "Zset/MecaSequential/cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    Nnode = mesh.GetInternalStorage().GetNumberOfNodes()
    dim = mesh.GetInternalStorage().GetDimensionality()
    Ninteg = FE.ComputeNumberOfIntegrationPoints(mesh)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis("config", str)
    collectionProblemData.DefineQuantity("U")
    collectionProblemData.AddReducedOrderBasis("U", np.arange(2*dim*Nnode).reshape((2,dim*Nnode)))
    collectionProblemData.DefineQuantity("p")
    collectionProblemData.AddReducedOrderBasis("p", np.arange(3*Ninteg).reshape(3,Ninteg))

    solutionU = Solution.Solution("U", dim, Nnode, True)
    solutionU.AddCompressedSnapshots(np.ones(2), 0.)
    solutionU.AddCompressedSnapshots(0.5+np.ones(2), 1.)
    solutionP = Solution.Solution("p", 1, Ninteg, False)
    solutionP.AddCompressedSnapshots(np.ones(3), 0.)
    solutionP.AddCompressedSnapshots(0.5+np.ones(3), 1.)

    problemData = ProblemData.ProblemData("myProblem")
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionP)


    folder = GetTestPath() + os.sep + 'Modules/Safran/IO/'

    ZSW.WriteZsetSolution(mesh, os.path.relpath(meshFileName, start=folder), folder+'ZsetSolutionWriter1',\
       collectionProblemData, problemData, "U")

    ZSW.WriteZsetSolution(mesh, os.path.relpath(meshFileName, start=folder), folder+'ZsetSolutionWriter2',\
       collectionProblemData, problemData, "U", outputReducedOrderBasis = True)

    assert filecmp.cmp(folder+"ZsetSolutionWriter1.ut",   folder+"ref/ZsetSolutionWriter1.ut",   shallow=False) == True
    assert filecmp.cmp(folder+"ZsetSolutionWriter1.integ",folder+"ref/ZsetSolutionWriter1.integ",shallow=False) == True
    assert filecmp.cmp(folder+"ZsetSolutionWriter1.node", folder+"ref/ZsetSolutionWriter1.node", shallow=False) == True
    assert filecmp.cmp(folder+"ZsetSolutionWriter2.ut",   folder+"ref/ZsetSolutionWriter2.ut",   shallow=False) == True
    assert filecmp.cmp(folder+"ZsetSolutionWriter2.integ",folder+"ref/ZsetSolutionWriter2.integ",shallow=False) == True
    assert filecmp.cmp(folder+"ZsetSolutionWriter2.node", folder+"ref/ZsetSolutionWriter2.node", shallow=False) == True

    os.system("rm -rf "+folder+"ZsetSolutionWriter1.ut "+folder+"ZsetSolutionWriter1.integ "+folder+"ZsetSolutionWriter1.node")
    os.system("rm -rf "+folder+"ZsetSolutionWriter2.ut "+folder+"ZsetSolutionWriter2.integ "+folder+"ZsetSolutionWriter2.node")


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
