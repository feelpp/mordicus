# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
from Mordicus.Modules.Safran.Containers.Loadings import Temperature as T
from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from Mordicus.Modules.Safran.Containers.OperatorCompressionData import OperatorCompressionDataMechanical as OCDM



def test():


    loading = T.Temperature("U", "ALLELEMENT")

    assert loading.GetSet() == "ALLELEMENT"
    assert loading.GetType() == "temperature"
    assert loading.GetSolutionName() == "U"
    assert loading.GetIdentifier() == ("U","temperature","ALLELEMENT")


    fields = {}

    fieldsMapTimes = [0., 1., 2.]
    fieldsMapValues = ["temperature1", "temperature1", "temperature2"]


    fields["temperature1"] = np.arange(12)
    fields["temperature2"] = np.ones(12)

    loading.SetFieldsMap(fieldsMapTimes, fieldsMapValues)
    loading.SetFields(fields)


    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[2, 3, 2], spacing=[2.0, 2.0, 2.0], ofTetras=True))

    dummy = 1
    operatorCompressionData = OCDM.OperatorCompressionDataMechanical("U", dummy, dummy, dummy)
    operatorCompressionData.SetReducedIntegrationPoints(np.array([1, 6, 9]))

    loading.ReduceLoading(mesh, operatorCompressionData = operatorCompressionData)

    np.testing.assert_almost_equal(loading.phiAtReducedIntegPoint.todense(),np.array([
     [0.25, 0.,   0.25, 0.25, 0.  , 0. ,  0. ,  0. ,  0. ,  0.25, 0.  , 0.  ],
     [0.  , 0.,   0.25, 0.  , 0.25, 0. ,  0. ,  0. ,  0. ,  0.  , 0.25, 0.25],
     [0.  , 0.,   0.25, 0.25, 0.  , 0. ,  0. ,  0. ,  0. ,  0.25, 0.  , 0.25]]))


    np.testing.assert_almost_equal(loading.fieldsAtReducedIntegrationPoints["temperature1"], np.array([3.5, 6.75, 6.25]))
    np.testing.assert_almost_equal(loading.fieldsAtReducedIntegrationPoints["temperature2"], np.array([1., 1., 1.]))

    np.testing.assert_almost_equal(loading.GetTemperatureAtReducedIntegrationPointsAtTime(0.2), np.array([3.5, 6.75, 6.25]))


    loading.UpdateLoading(loading)

    #dummy = 1.
    #loading.HyperReduceLoading(mesh, dummy, dummy, dummy)

    assert loading.ComputeContributionToReducedExternalForces(0.2) == 0.

    loading.__getstate__()

    print(loading)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
