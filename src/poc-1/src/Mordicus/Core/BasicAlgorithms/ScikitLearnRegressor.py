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
    model = GridSearchCV(estimator = regressor, param_grid = paramGrid, scoring = 'neg_mean_squared_error', cv = 4, verbose = 2, n_jobs=-1)
    model.fit(X, y)
    
    return model, scalerX, scalery





def ComputeRegressionApproximation(model, scalerX, scalery, XTest):

    XTest = scalerX.transform(XTest)
    yTest = model.predict(XTest)
    yTest = scalery.inverse_transform(yTest)

    return yTest




if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

