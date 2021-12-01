# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.BasicAlgorithms import ScikitLearnRegressor as SLR

def test():

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF, ConstantKernel
    #from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(0.01, 10.0)) * RBF(length_scale_bounds=(1e-2, 1e2)) + WhiteKernel(noise_level_bounds=(1e-10, 1e0))

    #regressor = GaussianProcessRegressor(kernel=kernel)
    regressor = SLR.MyGPR(kernel=kernel)
    paramGrids = {'kernel__k1__k1__constant_value':[0.1, 1.], 'kernel__k1__k2__length_scale': [1., 10.], 'kernel__k2__noise_level': [1., 2.]}

    X = np.array([[1.0, 1.0, 0.5, 0.25],[1.0, 1.5, 0.5, 0.25],[2.0, 0.5, 1.0, 0.9],[2.0, 2.0, 1.0, 0.9]])
    y = np.array([[1.0, 1.0],[1.0, 1.5],[2.0, 0.5],[2.0, 2.0]])

    model, scalerX, scalery = SLR.GridSearchCVRegression(regressor, paramGrids, X, y)
    SLR.ComputeRegressionApproximation(model, scalerX, scalery, X)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover