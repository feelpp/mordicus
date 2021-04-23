# -*- coding: utf-8 -*-


def GridSearchCVRegression(regressor, paramGrid, X, y):
    """
    Optimizes a scikit learn regressor using gridSearchCV, using training data and target values

    Parameters
    ----------
    regressor : objects satisfying the scikit-learn regressors API
        input regressor to be fitted and optimized
    paramGrid : float
        the truncation tolerence, determining the number of keps eigenvalues
    X : np.ndarray
        training data
    y : np.ndarray
        target values

    Returns
    -------
    np.ndarray
        kept eigenvalues, of size (numberOfEigenvalues)
    np.ndarray
        kept eigenvectors, of size (numberOfEigenvalues, numberOfSnapshots)
    """


    from sklearn import preprocessing


    scalerX = preprocessing.StandardScaler()#MinMaxScaler()
    scalery = preprocessing.StandardScaler()#MinMaxScaler()

    scalerX.fit(X)
    scalery.fit(y)

    X = scalerX.transform(X)
    y = scalery.transform(y)


    from sklearn.model_selection import GridSearchCV
    #model = GridSearchCV(estimator = regressor, param_grid = paramGrid, scoring = 'neg_mean_squared_error', cv = 4, verbose = 2, n_jobs=-1)
    model = GridSearchCV(estimator = regressor, param_grid = paramGrid, cv = 4, verbose = 2, n_jobs=-1)
    model.fit(X, y)

    return model, scalerX, scalery





def ComputeRegressionApproximation(model, scalerX, scalery, XTest):

    XTest = scalerX.transform(XTest)
    yTest = model.predict(XTest)
    yTest = scalery.inverse_transform(yTest)

    return yTest


from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.utils.optimize import _check_optimize_result
import scipy

class MyGPR(GaussianProcessRegressor):
    def __init__(self, kernel):
        super().__init__(kernel)

    def _constrained_optimization(self, obj_func, initial_theta, bounds):
        if self.optimizer == "fmin_l_bfgs_b":
            opt_res = scipy.optimize.minimize(obj_func, initial_theta, method="L-BFGS-B", jac=True, bounds=bounds, options={'maxiter':10000000000, 'gtol': 1.e-6})
            _check_optimize_result("lbfgs", opt_res)
            theta_opt, func_min = opt_res.x, opt_res.fun
        elif callable(self.optimizer):# pragma: no cover
            theta_opt, func_min = self.optimizer(obj_func, initial_theta, bounds=bounds)
        else:# pragma: no cover
            raise ValueError("Unknown optimizer %s." % self.optimizer)
        return theta_opt, func_min




if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

