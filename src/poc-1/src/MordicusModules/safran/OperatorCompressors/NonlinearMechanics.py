# -*- coding: utf-8 -*-
import numpy as np


def OnlineComputeRegression(
    onlineProblemData, operatorCompressionOutputData, compressedSnapshots
):
    """
    Compute the online stage using the method of POD on the snapshots and a regression on the coefficients
    
    The parameters must have been initialized in onlineProblemData
    The time sequence in compressedSnapshots must have been initialized
    This function set the attribute "coefficients" of compressedSnapshots
    
    Parameters
    ----------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object 
    compressedSnapshots : ModesAndCoefficients
        compressed solution whose attribute "coefficients" is set
    """

    1.0


def OperatorCompressionOffline(
    collectionProblemData, solutionName, operatorCompressionInputData
):
    """
    Computes the offline operator compression stage using the method of POD on the snapshots and a regression on the coefficients
    
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object 
    solutionName : str
        name of the solution to be treated
    operatorCompressionInputData : class satisfying the scikit-learn regressors API
        input regressor to be fitted
                
    Returns
    -------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    """
    assert isinstance(solutionName, str)

    return 1.0
