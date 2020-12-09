# -*- coding: utf-8 -*-
import os
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
    dataType : string ("scalar" or "vector")
    initialSnapshot : float or np.ndarray of size (numberOfDofs,)
    reducedInitialSnapshot : np.ndarray of size (numberOfModes,)

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


    def ReduceInitialSnapshot(self, solutionName, reducedOrderBasis, snapshotCorrelationOperator):

        assert isinstance(reducedOrderBasis, np.ndarray)

        if self.dataType[solutionName] == "scalar":
            if self.initialSnapshot[solutionName] == 0.:
                self.SetReducedInitialSnapshot(solutionName, np.zeros(reducedOrderBasis.shape[0]))
                return

            else:
                initVector = self.initialSnapshot[solutionName] * np.ones(reducedOrderBasis.shape[1])

        else:
            initVector = self.initialSnapshot[solutionName]# pragma: no cover


        matVecProduct = snapshotCorrelationOperator.dot(initVector)

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
