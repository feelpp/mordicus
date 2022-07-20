# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import numpy as np
import pytest
from Mordicus.Core.BasicAlgorithms import ScikitLearnRegressor as SLR

def test_ScikitLearnRegressor():

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF, ConstantKernel
    #from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(0.01, 10.0)) * RBF(length_scale_bounds=(1e-2, 1e2)) + WhiteKernel(noise_level_bounds=(1e-10, 1e0))

    #regressor = GaussianProcessRegressor(kernel=kernel)
    regressor = SLR.MyGPR(kernel=kernel)
    paramGrids = {'kernel__k1__k1__constant_value':[0.1, 1.], 'kernel__k1__k2__length_scale': [1., 10.], 'kernel__k2__noise_level': [1., 2.]}

    X = np.array([[1.0, 1.0, 0.5, 0.25],[1.0, 1.5, 0.5, 0.25],[2.0, 0.5, 1.0, 0.9],[2.0, 2.0, 1.0, 0.9]])
    y = np.array([[1.0, 1.0],[1.0, 1.5],[2.0, 0.5],[2.0, 2.0]])

    model, scalerX, scalery = SLR.GridSearchCVRegression(regressor, paramGrids, X, y)
    yPred = SLR.ComputeRegressionApproximation(model, scalerX, scalery, X)

    yPredRef = np.array([[1.00000037, 1.00000134],
                         [1.00000037, 1.49999866],
                         [1.9999994 , 0.50000105],
                         [1.9999994 , 1.99999895]])

    np.testing.assert_almost_equal(yPred, yPredRef)

    return "ok"


if __name__ == "__main__":
    print(test_ScikitLearnRegressor())  # pragma: no cover
