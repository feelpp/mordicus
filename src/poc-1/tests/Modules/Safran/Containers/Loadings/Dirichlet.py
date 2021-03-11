# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.Loadings import Dirichlet as D
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath

import numpy as np


def test():

    loading = D.Dirichlet("U", "x0")
    
    def boundaryValue(x):
        return x
    
    loading.SetFunction(boundaryValue)
    


    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"

    mesh = ZMR.ReadMesh(meshFileName)
    nbDofs = mesh.GetNumberOfNodes()*mesh.GetDimensionality()
    
    reducedOrderBases = {"U":np.random.rand(2, nbDofs)}
    dummy = 1
    loading.ReduceLoading(mesh, dummy, reducedOrderBases, dummy)
    

    loading.ComputeContributionToReducedExternalForces(0.2)    
    
    
    loading.__getstate__()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
