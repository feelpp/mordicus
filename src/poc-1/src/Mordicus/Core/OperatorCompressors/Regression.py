# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np
from Mordicus.Core.BasicAlgorithms import  ScikitLearnRegressor as SLR


def ComputeOnline(
    onlineProblemData, solutionName, operatorCompressionOutputData
):
    """
    Compute the online stage using the method of POD on the snapshots and a regression on the coefficients

    The parameters must have been initialized in onlineProblemData

    Parameters
    ----------
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object
    solutionName : str
        names of the solution to be treated
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)

    Returns
    -------
    collections.OrderedDict
        onlineCompressedSnapshots; dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """
    regressor = operatorCompressionOutputData[solutionName][0]
    scalerParameter = operatorCompressionOutputData[solutionName][1]
    scalerCoefficients = operatorCompressionOutputData[solutionName][2]

    onlineParameters = onlineProblemData.GetParametersList()


    onlineCoefficients = SLR.ComputeRegressionApproximation(regressor, scalerParameter, scalerCoefficients, onlineParameters)

    timeSequence = onlineProblemData.GetParametersTimeSequence()


    import collections
    onlineCompressedSnapshots = collections.OrderedDict()

    for i, time in enumerate(timeSequence):
        onlineCompressedSnapshots[time] = onlineCoefficients[i,:]

    return onlineCompressedSnapshots


def CompressOperator(
    collectionProblemData, solutionNames, operatorCompressionInputData
):
    """
    Computes the offline operator compression stage using the method of POD on the snapshots and a regression on the coefficients

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    solutionNames : list of str
        names of the solution to be treated
    operatorCompressionInputData : dict of objects satisfying the scikit-learn regressors API
        input regressor to be fitted
    """

    operatorCompressionData = {}

    regressors = operatorCompressionInputData[0]
    paramGrids = operatorCompressionInputData[1]

    for solutionName in solutionNames:


        regressor = regressors[solutionName]
        paramGrid = paramGrids[solutionName]

        numberOfModes = collectionProblemData.GetReducedOrderBasisNumberOfModes(solutionName)
        numberOfSnapshots = collectionProblemData.GetGlobalNumberOfSnapshots(solutionName)
        parameterDimension = collectionProblemData.GetParameterDimension()

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


        model, scalerParameter, scalerCoefficients = SLR.GridSearchCVRegression(regressor, paramGrid, parameters, coefficients)

        operatorCompressionData[solutionName] = (model, scalerParameter, scalerCoefficients)

    collectionProblemData.SetOperatorCompressionData(operatorCompressionData)



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


