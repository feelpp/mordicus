# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
from Mordicus.Modules.Safran.Containers.Loadings import PressureBC as PBC
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath


def test():

    loading = PBC.PressureBC("U", "x0")

    assert loading.GetSet() == "x0"
    assert loading.GetType() == "pressure"
    assert loading.GetSolutionName() == "U"
    assert loading.GetIdentifier() == ("U","pressure","x0")

    coefficients = {}
    fieldsMap    = {}
    fields       = {}

    coefficients[0.0] = 1.0
    coefficients[1.0] = 1.5
    coefficients[2.0] = 0.2

    fieldsMap[0.0] = "pressure1"
    fieldsMap[1.0] = "pressure2"
    fieldsMap[2.0] = "pressure1"

    fields["pressure1"] = np.arange(36)
    fields["pressure2"] = np.ones(36)



    loading.SetCoefficients(coefficients)
    loading.SetFieldsMap(fieldsMap)
    loading.SetFields(fields)

    assert id(loading.GetFields()) == id(fields)

    folder = GetTestDataPath() + "Zset/MecaSequential/"
    meshFileName = folder + "cube.geof"

    mesh = ZMR.ReadMesh(meshFileName)

    nbDofs = mesh.GetNumberOfNodes()*mesh.GetDimensionality()
    reducedOrderBases = {"U":np.arange(2*nbDofs).reshape((2,-1))}
    dummy = 1

    loading.ReduceLoading(mesh, dummy, reducedOrderBases, dummy)

    assembledReducedFields = loading.assembledReducedFields
    np.testing.assert_almost_equal(1e-3*assembledReducedFields["pressure1"],\
                                   1e-3*np.array([-3817.91666667, -21825.41666667]))
    np.testing.assert_almost_equal(1e-3*assembledReducedFields["pressure2"],\
                                   1e-3*np.array([-168., -1197.]))


    np.testing.assert_almost_equal(1e-3*loading.GetAssembledReducedFieldAtTime(0.2),\
                                   1e-3*np.array([-3396.72666667, -19469.70666667]))

    #loading.HyperReduceLoading(mesh, dummy, reducedOrderBases, dummy)
    loading.__getstate__()


    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
