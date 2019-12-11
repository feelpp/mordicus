# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.Containers.CompressedFormats import ModesAndCoefficients as MAC


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
    regressor = operatorCompressionOutputData[0]
    scalerParameter = operatorCompressionOutputData[1]
    scalerCoefficients = operatorCompressionOutputData[2]

    timeSequence = compressedSnapshots.GetTimes()

    onlineParameters = np.array(
        [onlineProblemData.GetParameterAtTime(t) for t in timeSequence]
    )

    onlineParameters = scalerParameter.transform(onlineParameters)
    onlineCoefficients = regressor.predict(onlineParameters)
    onlineCoefficients = scalerCoefficients.inverse_transform(onlineCoefficients)

    compressedSnapshots.SetCoefficients(onlineCoefficients)


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
        times = (
            problemData.GetSolution(solutionName).GetCompressedSnapshots().GetTimes()
        )

        coefficients[count : count + localNumberOfSnapshots, :] = (
            problemData.GetSolution(solutionName)
            .GetCompressedSnapshots()
            .GetCoefficients()
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

    operatorCompressionOutputData = (regressor, scalerParameter, scalerCoefficients)

    return operatorCompressionOutputData
