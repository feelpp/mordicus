# -*- coding: utf-8 -*-

import numpy as np
import collections
from Mordicus.Modules.Safran.Containers.Loadings import Radiation as R
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath


def test():

    loading = R.Radiation("set1")

    Text = collections.OrderedDict()
    for i in range(3):
        Text[float(i)] = 1.

    loading.SetText(Text)
    loading.SetStefanBoltzmannConstant(2.)
    loading.GetTextAtTime(0.5)

    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"

    mesh = ZMR.ReadMesh(meshFileName)

    dummy = 1
    loading.ReduceLoading(mesh, dummy, np.ones((2,3)), dummy)

    loading.ComputeContributionToReducedExternalForces(0.2)

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
