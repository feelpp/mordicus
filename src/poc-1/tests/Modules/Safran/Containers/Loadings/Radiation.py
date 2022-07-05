# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
from Mordicus.Modules.Safran.Containers.Loadings import Radiation as R
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath


def test():

    loading = R.Radiation("T", "x0")

    assert loading.GetSet() == "x0"
    assert loading.GetType() == "radiation"
    assert loading.GetSolutionName() == "T"
    assert loading.GetIdentifier() == ("T","radiation","x0")


    Text = {0.:1.,0.2:0.5,1.:1.2}

    loading.SetText(Text)
    loading.SetStefanBoltzmannConstant(2.)
    assert loading.GetTextAtTime(0.4) == 0.675

    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"
    mesh = ZMR.ReadMesh(meshFileName)
    reducedOrderBases = {"T":np.arange(2*mesh.GetNumberOfNodes()).reshape((2,-1))}

    dummy = 1
    loading.ReduceLoading(mesh, dummy, reducedOrderBases, dummy)

    np.testing.assert_almost_equal(0.01*loading.reducedPhiT, 0.01*np.array([168., 511.]))
    np.testing.assert_almost_equal(0.1*loading.ComputeContributionToReducedExternalForces(0.2), 0.1*np.array([21., 63.875]))

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
