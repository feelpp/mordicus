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

from Mordicus.Core.Containers.InitialConditions.InitialConditionBase import InitialConditionBase
from mpi4py import MPI


class InitialCondition(InitialConditionBase):
    """
    Class modeling an initial condition

    Attributes
    ----------
    dataType : dict
        dictionary with solutionName (str) as keys and the type of initial
        condition (str: "scalar" or "vector")
    initialSnapshot : dict
        dictionary with solutionName (str) as keys and the values of the initial
        condition (float or np.ndarray of floats of size (numberOfDofs,))
    reducedInitialSnapshot : dict
        dictionary with solutionName (str) as keys and the values of the reduced
        initial snapshot (np.ndarray of floats of size (numberOfModes,))
    """

    def __init__(self):

        super(InitialCondition, self).__init__()

        self.dataType = {}
        self.initialSnapshot = {}
        self.reducedInitialSnapshot = {}


    def SetDataType(self, solutionName, dataTy):
        """
        Sets the type of initial condition

        Parameters
        ----------
        solutionName : str
            name of the corresponding solution
        dataTy : str
            type of initial condition (scalar" or "vector")
        """
        self.dataType[solutionName] = dataTy


    def GetDataType(self, solutionName):
        """
        Returns the type of initial condition for a given solutionName

        Returns
        -------
        str
            type of initial condition (scalar" or "vector")
        """
        return self.dataType[solutionName]


    def SetInitialSnapshot(self, solutionName, initialSnapshot):
        """
        Sets the initial condition

        Parameters
        ----------
        solutionName : str
            name of the corresponding solution
        initialSnapshot : float or np.ndarray of floats of size (numberOfDofs,)
            values of the initial condition
        """
        self.initialSnapshot[solutionName] = initialSnapshot


    def SetReducedInitialSnapshot(self, solutionName, reducedInitialSnapshot):
        """
        Sets the reduced initial snapshot

        Parameters
        ----------
        solutionName : str
            name of the corresponding solution
        reducedInitialSnapshot : np.ndarray of floats of size (numberOfModes,)
            values of the reduced initial snapshot
        """
        self.reducedInitialSnapshot[solutionName] = reducedInitialSnapshot


    def GetReducedInitialSnapshot(self, solutionName):
        """
        Returns the reduced initial snapshot

        Parameters
        ----------
        solutionName : str
            name of the corresponding solution

        Returns
        -------
        np.ndarray of floats of size (numberOfModes,)
            values of the reduced initial snapshot
        """
        return self.reducedInitialSnapshot[solutionName]


    def ReduceInitialSnapshot(self, reducedOrderBases, snapshotCorrelationOperator = None):
        """
        Computes and sets the reduced initial snapshot

        Parameters
        ----------
        reducedOrderBases : dict(str: np.ndarray)
            dictionary with solutionNames (str) as keys and reducedOrderBases
            (np.ndarray of size (numberOfModes, numberOfDOFs)) as values
        snapshotCorrelationOperator : scipy.sparse.csr, optional
            correlation operator between the snapshots
        """
        for solutionName in self.initialSnapshot.keys():

            reducedOrderBasis = reducedOrderBases[solutionName]

            if self.dataType[solutionName] == "scalar":
                if self.initialSnapshot[solutionName] == 0.:
                    self.SetReducedInitialSnapshot(solutionName, np.zeros(reducedOrderBasis.shape[0]))
                    continue

                else:
                    initVector = self.initialSnapshot[solutionName] * np.ones(reducedOrderBasis.shape[1])

            else:
                initVector = self.initialSnapshot[solutionName]


            if snapshotCorrelationOperator is None:
                matVecProduct = initVector
            else:
                matVecProduct = snapshotCorrelationOperator[solutionName].dot(initVector)

            localScalarProduct = np.dot(reducedOrderBasis, matVecProduct)
            globalScalarProduct = np.zeros(localScalarProduct.shape)
            MPI.COMM_WORLD.Allreduce([localScalarProduct, MPI.DOUBLE], [globalScalarProduct, MPI.DOUBLE])

            self.SetReducedInitialSnapshot(solutionName, globalScalarProduct)


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