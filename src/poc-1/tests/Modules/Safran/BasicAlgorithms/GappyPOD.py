# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP


def test():

    modesAtMask = np.array([[1., 0., 0.], [0., 1., 0.]])
    fieldAtMask = np.array([1., 0., 1.])

    np.testing.assert_almost_equal(GP.Fit(modesAtMask, fieldAtMask), [1., 0.])

    res, cost = GP.FitAndCost(modesAtMask, fieldAtMask)
    np.testing.assert_almost_equal(res, [1., 0.])
    np.testing.assert_almost_equal(cost, 0.35355339059327373)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
