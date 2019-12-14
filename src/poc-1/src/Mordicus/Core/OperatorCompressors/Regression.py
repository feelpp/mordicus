# -*- coding: utf-8 -*-
import numpy as np


def ComputeApproximation(
    onlineProblemData, operatorCompressionOutputData
):
    """
    Compute the online stage using the method of POD on the snapshots and a regression on the coefficients
    
    The parameters must have been initialized in onlineProblemData
    
    Parameters
    ----------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object 
        
    Returns
    -------
    collections.OrderedDict
        onlineCompressedSolution; dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """
    regressor = operatorCompressionOutputData[0]
    scalerParameter = operatorCompressionOutputData[1]
    scalerCoefficients = operatorCompressionOutputData[2]

    timeSequence = onlineProblemData.GetParametersTimeSequence()

    onlineParameters = onlineProblemData.GetParametersList()

    onlineParameters = scalerParameter.transform(onlineParameters)
    onlineCoefficients = regressor.predict(onlineParameters)
    onlineCoefficients = scalerCoefficients.inverse_transform(onlineCoefficients)

    import collections
    onlineCompressedSolution = collections.OrderedDict()

    for i, time in enumerate(timeSequence):
        onlineCompressedSolution[time] = onlineCoefficients[i,:]
        
    return onlineCompressedSolution


def CompressOperator(
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
    """
    assert isinstance(solutionName, str)

    regressor = operatorCompressionInputData

    numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes(
        solutionName
    )
    numberOfSnapshots = collectionProblemData.GetGlobalNumberOfSnapshots(solutionName)
    parameterDimension = collectionProblemData.GetParameterDimension()

    # print("numberOfModes      =", numberOfModes)
    # print("numberOfSnapshots  =", numberOfSnapshots)
    # print("parameterDimension =", parameterDimension)

    coefficients = np.zeros((numberOfSnapshots, numberOfModes))
    parameters = np.zeros((numberOfSnapshots, parameterDimension))

    count = 0
    for key, problemData in collectionProblemData.GetProblemDatas().items():

        localNumberOfSnapshots = problemData.GetSolution(
            solutionName
        ).GetNumberOfSnapshots()
        
        times = problemData.GetSolution(solutionName).GetTimeSequenceFromCompressedSnapshots()

        coefficients[count : count + localNumberOfSnapshots, :] = (
            problemData.GetSolution(solutionName).GetCompressedSnapshotsList()
        )

        localParameters = np.array([problemData.GetParameterAtTime(t) for t in times])
        parameters[count : count + localNumberOfSnapshots, :] = localParameters

        count += localNumberOfSnapshots

    from sklearn.preprocessing import MinMaxScaler

    scalerParameter = MinMaxScaler()
    scalerCoefficients = MinMaxScaler()

    scalerParameter.fit(parameters)
    scalerCoefficients.fit(coefficients)

    parameters = scalerParameter.transform(parameters)
    coefficients = scalerCoefficients.transform(coefficients)

    regressor.fit(parameters, coefficients)

    collectionProblemData.SetOperatorCompressionData((regressor, scalerParameter, scalerCoefficients))
