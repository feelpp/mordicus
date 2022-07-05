# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#



def GridSearchCVRegression(regressor, paramGrid, X, y):
    """
    Optimizes a scikit learn regressor using gridSearchCV, using training data and target values

    Parameters
    ----------
    regressor : object satisfying the scikit-learn regressors API
        input regressor to be fitted and optimized
    paramGrid : dict
        of lists (of floats) containing hyperparameter values of the considered
        regressor
    X : np.ndarray
        training data
    y : np.ndarray
        target values

    Returns
    -------
    sklearn.model_selection._search.GridSearchCV
        trained and optimized scikit learn regressor
    sklearn.preprocessing._data.StandardScaler
        scaler trained on input data
    sklearn.preprocessing._data.StandardScaler
        scaler trained on output data
    """

    from sklearn import preprocessing

    scalerX = preprocessing.StandardScaler()#MinMaxScaler()
    scalery = preprocessing.StandardScaler()#MinMaxScaler()

    scalerX.fit(X)
    scalery.fit(y)

    X = scalerX.transform(X)
    y = scalery.transform(y)

    verbose = 2
    cv = min(X.shape[0],4)

    if cv >1:

        from sklearn.model_selection import GridSearchCV
        #model = GridSearchCV(estimator = regressor, param_grid = paramGrid, scoring = 'neg_mean_squared_error', cv = 4, verbose = verbose, n_jobs=-1)
        model = GridSearchCV(estimator = regressor, param_grid = paramGrid, cv = cv, verbose = verbose, n_jobs=-1)
    else:# pragma: no cover
        model = regressor

    model.fit(X, y)

    return model, scalerX, scalery





def ComputeRegressionApproximation(model, scalerX, scalery, XTest):
    """
    Computes the prediction of the Regressor,taking into account prelearned scalers for input and output

    Parameters
    ----------
    model : sklearn.model_selection._search.GridSearchCV
        trained and optimized scikit learn regressor
    scalerX : sklearn.preprocessing._data.StandardScaler
        scaler trained on input data
    scalery : sklearn.preprocessing._data.StandardScaler
        scaler trained on output data
    XTest : np.ndarray
        testing data

    Returns
    -------
    np.ndarray
        kept eigenvalues, of size (numberOfEigenvalues)
    np.ndarray
        kept eigenvectors, of size (numberOfEigenvalues, numberOfSnapshots)
    """

    XTest = scalerX.transform(XTest)
    yTest = model.predict(XTest)
    yTest = scalery.inverse_transform(yTest)

    return yTest


from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.utils.optimize import _check_optimize_result
import scipy

class MyGPR(GaussianProcessRegressor):
    """
    Customization of scikit-learn's GaussianProcessRegressor
    """
    def __init__(self, kernel):
        super().__init__(kernel)

    def _constrained_optimization(self, obj_func, initial_theta, bounds):
        if self.optimizer == "fmin_l_bfgs_b":
            opt_res = scipy.optimize.minimize(obj_func, initial_theta, method="L-BFGS-B", jac=True, bounds=bounds, options={'maxiter':int(1.e9), 'gtol': 1.e-5})
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

