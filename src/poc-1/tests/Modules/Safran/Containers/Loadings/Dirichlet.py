# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.Loadings import Dirichlet as D
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath


import numpy as np


def test():

    loading = D.Dirichlet("U", "x0")

    assert loading.GetSet() == "x0"
    assert loading.GetType() == "dirichlet"
    assert loading.GetSolutionName() == "U"
    assert loading.GetIdentifier() == ("U","dirichlet","x0")

    def boundaryValue(x):
        return x

    loading.SetFunction(boundaryValue)

    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"

    mesh = ZMR.ReadMesh(meshFileName)
    nbDofs = mesh.GetNumberOfNodes()*mesh.GetDimensionality()

    reducedOrderBases = {"U":np.arange(2*nbDofs).reshape((2,-1))}
    dummy = 1
    loading.ReduceLoading(mesh, dummy, reducedOrderBases, dummy)

    np.testing.assert_almost_equal(1e-3*loading.GetAssembledReducedFieldAtTime(0.2), 1e-3*np.array([710.5, 1739.5]))
    np.testing.assert_almost_equal(1e-5*loading.ComputeContributionToReducedExternalForces(0.2), 1e-5*np.array([710500., 1739500.]))

    #loading.HyperReduceLoading(mesh, dummy, reducedOrderBases, dummy)

    loading.__getstate__()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
