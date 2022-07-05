# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.OperatorCompressionData import OperatorPreCompressionDataMechanical as OPCDM

import numpy as np

def test():


    gradPhiAtIntegPoint = np.arange(12).reshape(3,4)
    integrationWeights = np.ones(3)

    operatorPreCompressionDataMechanical = OPCDM.OperatorPreCompressionDataMechanical("U", gradPhiAtIntegPoint, integrationWeights, [["A"],["A", "B"],["B"]])

    assert operatorPreCompressionDataMechanical.GetListOfTags() == [["A"],["A", "B"],["B"]]
    assert operatorPreCompressionDataMechanical.GetNumberOfIntegrationPoints() == 3
    np.testing.assert_almost_equal(operatorPreCompressionDataMechanical.GetIntegrationWeights(), np.ones(3))
    np.testing.assert_almost_equal(operatorPreCompressionDataMechanical.GetGradPhiAtIntegPoint(), np.arange(12).reshape(3,4))


    operatorPreCompressionDataMechanical.__getstate__()

    print(operatorPreCompressionDataMechanical)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


