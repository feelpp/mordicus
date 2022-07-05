# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
from Mordicus.Modules.Safran.Containers.Loadings import ConvectionHeatFlux as CHF
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath

def test():

    loading = CHF.ConvectionHeatFlux("T", "x0")

    assert loading.GetSet() == "x0"
    assert loading.GetType() == "convection_heat_flux"
    assert loading.GetSolutionName() == "T"
    assert loading.GetIdentifier() == ("T","convection_heat_flux","x0")

    h    = {}
    Text = {}

    timeSequence = [0., 0.5, 0.8, 1.8]
    for i, time in enumerate(timeSequence):
        h[time]    = 1.1*i
        Text[time] = 2.2*i

    loading.SetH(h)
    loading.SetText(Text)
    assert loading.GetCoefficientsAtTime(0.25) == (0.55, 1.1)

    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"

    mesh = ZMR.ReadMesh(meshFileName)

    reducedOrderBases = {"T":np.arange(2*mesh.GetNumberOfNodes()).reshape((2,-1))}
    dummy = 1

    loading.ReduceLoading(mesh, dummy, reducedOrderBases, dummy)

    np.testing.assert_almost_equal(1e-5*loading.reducedPhiTPhiT, 1e-5*np.array([[35574., 93198.], [93198., 268471.]]))
    np.testing.assert_almost_equal(1e-2*loading.reducedPhiT, 1e-2*np.array([168., 511.]))
    np.testing.assert_almost_equal(1e-2*loading.ComputeContributionToReducedExternalForces(0.2), 1e-2*np.array([65.0496, 197.8592]))

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
