# -*- coding: utf-8 -*-
import numpy as np
import os
#from mpi4py import MPI
import collections
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA


"""
Description of operatorCompressionData: dict of keys


"""





def PrepareOnline(onlineProblemData, timeSequence, reducedOrderBasis, operatorCompressionData):
    """
    1.
    """

    onlineCompressedSolution = collections.OrderedDict()
    for time in timeSequence:
        onlineCompressedSolution[time] = np.zeros(reducedOrderBasis.shape[0])


    return onlineCompressedSolution




def ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasis, operatorCompressionData, tolerance):
    """
    Compute the online stage using the method POD and ECM for a thermal problem

    The parameters must have been initialized in onlineProblemData
    """


    currentFolder = os.getcwd()
    folder = currentFolder + os.sep + onlineProblemData.GetDataFolder()
    os.chdir(folder)


    onlineCompressedSolution = PrepareOnline(onlineProblemData, timeSequence, reducedOrderBasis, operatorCompressionData)

    for timeStep in range(1, len(timeSequence)):

        previousTime = timeSequence[timeStep-1]
        time = timeSequence[timeStep]
        dtime = time - previousTime



        print("time =", time)

        normRes = 1.e-16

        count = 0
        while normRes > tolerance:

            count += 1 # pragma: no cover
            if count == 20: # pragma: no cover
                raise("problem could not converge after 20 iterations") # pragma: no cover


        print("=== Newton iterations:", count)

    os.chdir(currentFolder)


    return onlineCompressedSolution







def CompressOperator(
    collectionProblemData, mesh, tolerance
):
    """
    Operator Compression for the POD and ECM for a thermal problem

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object
    mesh : MeshBase
        mesh
    tolerance : float
        tolerance for Empirical Cubature Method

    Returns
    -------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    """



    operatorCompressionData = {}

    collectionProblemData.SetOperatorCompressionData(operatorCompressionData)



