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
from Mordicus.Core.Containers.OperatorCompressionData import OperatorCompressionDataRegression as OCDR


def ComputeOnline(onlineProblemData, solutionName):
    """
    Compute the online stage using the method of POD on the snapshots and a regression on the coefficients

    The parameters must have been initialized in onlineProblemData

    Parameters
    ----------
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object
    solutionName : str
        names of the solution to be treated

    Returns
    -------
    collections.OrderedDict
        onlineCompressedSnapshots; dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """

    onlineData = onlineProblemData.GetOnlineData(solutionName)

    regressor = onlineData.GetModel()
    scalerParameter = onlineData.GetScalerParameters()
    scalerCoefficients = onlineData.GetScalerCoefficients()

    onlineParameters = onlineProblemData.GetParametersList()


    onlineCoefficients = SLR.ComputeRegressionApproximation(regressor, scalerParameter, scalerCoefficients, onlineParameters)

    timeSequence = onlineProblemData.GetParametersTimeSequence()


    import collections
    onlineCompressedSnapshots = collections.OrderedDict()

    for i, time in enumerate(timeSequence):
        onlineCompressedSnapshots[time] = onlineCoefficients[i,:]

    return onlineCompressedSnapshots


def CompressOperator(collectionProblemData, regressors, paramGrids):
    """
    Computes the offline operator compression stage using the method of POD on the snapshots and a regression on the coefficients

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    regressors : dict of objects satisfying the scikit-learn regressors API
        input regressor to be fitted
    paramGrids : dict
        of dict with key: hyperparameter names and values: hyperparameter values to test
    """

    assert list(regressors.keys()) == list(paramGrids.keys())

    for solutionName in regressors.keys():

        operatorCompressionDataRegression = OCDR.OperatorCompressionDataRegression(solutionName)

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

        model, scalerParameters, scalerCoefficients = SLR.GridSearchCVRegression(regressor, paramGrid, parameters, coefficients)

        operatorCompressionDataRegression.SetModel(model)
        operatorCompressionDataRegression.SetScalerParameters(scalerParameters)
        operatorCompressionDataRegression.SetScalerCoefficients(scalerCoefficients)

        collectionProblemData.AddOperatorCompressionData(operatorCompressionDataRegression)



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


