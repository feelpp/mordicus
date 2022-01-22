# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.OperatorCompressionData import OperatorCompressionDataMechanical as OCDM
import numpy as np

def test():


    gradPhiAtIntegPoint = np.arange(12).reshape(3,4)
    integrationWeights = np.ones(3)

    operatorCompressionDataMechanical = OCDM.OperatorCompressionDataMechanical("U", gradPhiAtIntegPoint, integrationWeights, [["A"],["A", "B"],["B"]])

    assert operatorCompressionDataMechanical.GetListOfTags() == [["A"],["A", "B"],["B"]]
    assert operatorCompressionDataMechanical.GetNumberOfIntegrationPoints() == 3
    np.testing.assert_almost_equal(operatorCompressionDataMechanical.GetIntegrationWeights(), np.ones(3))
    np.testing.assert_almost_equal(operatorCompressionDataMechanical.GetGradPhiAtIntegPoint(), np.arange(12).reshape(3,4))

    operatorCompressionDataMechanical.SetReducedIntegrationPoints(np.arange(2))
    np.testing.assert_almost_equal(operatorCompressionDataMechanical.GetReducedIntegrationPoints(), np.arange(2))

    operatorCompressionDataMechanical.SetReducedIntegrationPoints(1.+np.ones(2))
    np.testing.assert_almost_equal(operatorCompressionDataMechanical.GetReducedIntegrationPoints(), 1.+np.ones(2))

    operatorCompressionDataMechanical.SetReducedIntegrationWeights(np.arange(2))
    np.testing.assert_almost_equal(operatorCompressionDataMechanical.GetReducedIntegrationWeights(), np.arange(2))

    operatorCompressionDataMechanical.SetReducedListOTags([["A"],["A", "B"]])
    assert operatorCompressionDataMechanical.GetReducedListOTags() == [["A"],["A", "B"]]

    operatorCompressionDataMechanical.SetReducedEpsilonAtReducedIntegPoints([["A"],["A", "B"]])
    assert operatorCompressionDataMechanical.GetReducedListOTags() == [["A"],["A", "B"]]


    operatorCompressionDataMechanical.SetReducedEpsilonAtReducedIntegPoints(np.ones((1,2,3)))
    np.testing.assert_almost_equal(operatorCompressionDataMechanical.GetReducedEpsilonAtReducedIntegPoints(), np.ones((1,2,3)))

    assert operatorCompressionDataMechanical.GetNumberOfSigmaComponents() == 1
    assert operatorCompressionDataMechanical.GetNumberOfReducedIntegrationPoints() == 2
    assert operatorCompressionDataMechanical.GetNumberOfModes() == 3

    operatorCompressionDataMechanical.SetDualReconstructionData({"GappyPOD": np.ones((3,2))})

    dualReconstructionData = operatorCompressionDataMechanical.GetDualReconstructionData()
    assert list(dualReconstructionData.keys()) == ["GappyPOD"]
    np.testing.assert_almost_equal(dualReconstructionData["GappyPOD"], np.ones((3,2)))

    operatorCompressionDataMechanical.__getstate__()

    print(operatorCompressionDataMechanical)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


