# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OperatorCompressionData import OperatorCompressionDataRegression as OCDR
from Mordicus.Core.BasicAlgorithms import  ScikitLearnRegressor as SLR
import numpy as np


def test():


    from sklearn.gaussian_process.kernels import WhiteKernel, RBF, ConstantKernel
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(0.01, 10.0)) * RBF(length_scale_bounds=(1e-2, 1e2)) + WhiteKernel(noise_level_bounds=(1e-10, 1e0))

    regressor = GaussianProcessRegressor(kernel=kernel)
    paramGrid = {'kernel__k1__k1__constant_value':[0.1, 1.], 'kernel__k1__k2__length_scale': [1., 10.], 'kernel__k2__noise_level': [1., 2.]}

    coefficients = np.ones((10, 3))
    parameters = np.ones((10, 2))

    model, scalerParameters, scalerCoefficients = SLR.GridSearchCVRegression(regressor, paramGrid, parameters, coefficients)

    operatorCompressionDataRegression = OCDR.OperatorCompressionDataRegression("U")

    operatorCompressionDataRegression.SetModel(model)
    operatorCompressionDataRegression.SetScalerParameters(scalerParameters)
    operatorCompressionDataRegression.SetScalerCoefficients(scalerCoefficients)


    assert id(operatorCompressionDataRegression.GetModel()) == id(model)
    assert id(operatorCompressionDataRegression.GetScalerParameters()) == id(scalerParameters)
    assert id(operatorCompressionDataRegression.GetScalerCoefficients()) == id(scalerCoefficients)

    print(operatorCompressionDataRegression)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


