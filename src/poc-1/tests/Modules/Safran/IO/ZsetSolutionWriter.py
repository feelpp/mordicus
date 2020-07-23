# -*- coding: utf-8 -*-

import numpy as np
import os
from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Modules.Safran.IO import ZsetSolutionWriter as ZSW
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.FE import FETools as FE
from Mordicus.Core import GetTestDataPath


def test():

    folder = GetTestDataPath() + "Zset/MecaSequential/"

    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)

    Nnode = mesh.GetInternalStorage().GetNumberOfNodes()
    dim = mesh.GetInternalStorage().GetDimensionality()
    Ninteg = FE.ComputeNumberOfIntegrationPoints(mesh)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.addVariabilityAxis("config", str)
    collectionProblemData.defineQuantity("U")
    collectionProblemData.AddReducedOrderBasis("U", np.random.rand(2,dim*Nnode))
    collectionProblemData.defineQuantity("p")
    collectionProblemData.AddReducedOrderBasis("p", np.random.rand(3,Ninteg))

    solutionU = Solution.Solution("U", dim, Nnode, True)
    solutionU.AddCompressedSnapshots(np.ones(2), 0.)
    solutionU.AddCompressedSnapshots(0.5+np.ones(2), 1.)
    solutionP = Solution.Solution("p", 1, Ninteg, False)
    solutionP.AddCompressedSnapshots(np.ones(3), 0.)
    solutionP.AddCompressedSnapshots(0.5+np.ones(3), 1.)

    problemData = ProblemData.ProblemData("toto")
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionP)



    ZSW.WriteZsetSolution(mesh, os.path.relpath(meshFileName), "test", collectionProblemData, problemData, "U")

    os.system("rm -rf toto.ut toto.integ toto.node")


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
