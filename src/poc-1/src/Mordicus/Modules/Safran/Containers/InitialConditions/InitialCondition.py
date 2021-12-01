# -*- coding: utf-8 -*-
import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from Mordicus.Core.Containers.InitialConditions.InitialConditionBase import InitialConditionBase
from mpi4py import MPI


class InitialCondition(InitialConditionBase):
    """

    Attributes
    ----------
    dataType : dict of string ("scalar" or "vector")
    initialSnapshot : dict of float or np.ndarray of size (numberOfDofs,)
    reducedInitialSnapshot : dict of np.ndarray of size (numberOfModes,)

    """

    def __init__(self):

        super(InitialCondition, self).__init__()

        self.dataType = {}
        self.initialSnapshot = {}
        self.reducedInitialSnapshot = {}


    def SetDataType(self, solutionName, dataType):

        self.dataType[solutionName] = dataType


    def GetDataType(self, solutionName):

        return self.dataType[solutionName]


    def SetInitialSnapshot(self, solutionName, initialSnapshot):

        self.initialSnapshot[solutionName] = initialSnapshot


    def SetReducedInitialSnapshot(self, solutionName, reducedInitialSnapshot):

        self.reducedInitialSnapshot[solutionName] = reducedInitialSnapshot


    def GetReducedInitialSnapshot(self, solutionName):

        return self.reducedInitialSnapshot[solutionName]


    def ReduceInitialSnapshot(self, reducedOrderBases, snapshotCorrelationOperator = None):

        for solutionName in self.initialSnapshot.keys():

            reducedOrderBasis = reducedOrderBases[solutionName]

            if self.dataType[solutionName] == "scalar":
                if self.initialSnapshot[solutionName] == 0.:
                    self.SetReducedInitialSnapshot(solutionName, np.zeros(reducedOrderBasis.shape[0]))
                    continue

                else:
                    initVector = self.initialSnapshot[solutionName] * np.ones(reducedOrderBasis.shape[1])

            else:
                initVector = self.initialSnapshot[solutionName]# pragma: no cover

            if snapshotCorrelationOperator is None:
                matVecProduct = initVector
            else:
                matVecProduct = snapshotCorrelationOperator[solutionName].dot(initVector)

            localScalarProduct = np.dot(reducedOrderBasis, matVecProduct)
            globalScalarProduct = np.zeros(reducedOrderBasis.shape[0])
            MPI.COMM_WORLD.Allreduce([localScalarProduct, MPI.DOUBLE], [globalScalarProduct, MPI.DOUBLE])

            self.SetReducedInitialSnapshot(solutionName, globalScalarProduct)# pragma: no cover




    def __getstate__(self):

        state = {}
        state["initialSnapshot"] = None
        state["reducedInitialSnapshot"] = self.reducedInitialSnapshot

        return state



    def __str__(self):
        res = "Initial Condition"
        return res

if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)