# -*- coding: utf-8 -*-

import numpy as np
import collections
from Mordicus.Modules.Safran.Containers.Loadings import ConvectionHeatFlux as CHF
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath

def test():

    loading = CHF.ConvectionHeatFlux("T", "set1")

    h = collections.OrderedDict()
    Text = collections.OrderedDict()

    timeSequence = [0., 1., 2., 3.]
    for time in timeSequence:
        h[time] = 1.
        Text[time] = 2.

    loading.SetH(h)
    loading.SetText(Text)
    loading.GetCoefficientsAtTime(0.5)

    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"

    mesh = ZMR.ReadMesh(meshFileName)


    reducedOrderBases = {"T":np.random.rand(2,3)}
    dummy = 1
    loading.ReduceLoading(mesh, dummy, reducedOrderBases, dummy)

    loading.ComputeContributionToReducedExternalForces(0.2)

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
