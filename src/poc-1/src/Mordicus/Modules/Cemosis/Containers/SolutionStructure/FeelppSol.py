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

import feelpp
from mpi4py import MPI
from petsc4py import PETSc

def energy(Mat, Vec):
    """ Comput the Vect*Mat*V """ 
    return Vec@(Mat@Vec)
    
class FeelppSolution(object):
    """
    Class containing a wrapping of element in Feelpp function space  

    Attributes
    ----------
    solutionName : str
        name of the solution field (e.g. "U", "T")
    nbeOfComponents : int
        number of components of the solution (e.g. 3 for "U" in 3D, or 1 for "T")
    numberOfNodes : int
        number of nodes for the geometrical support of the solution
    numberOfDOFs : int
        number of degrees of freedom 
    solution : feelpp sol 
        solution in feelpp format  
    reducedCoeff : dict 
        dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """

    def __init__(self, solutionName, nbeOfComponents, numberOfNodes):

        for attr, typ in zip(["solutionName", "nbeOfComponents", "numberOfNodes"], [str, int, int]):
            if not isinstance(locals()[attr], typ):#pragma: no cover
                raise TypeError("Attribute {0} should be of type {1}".format(attr, str(typ)))

        self.solutionName = solutionName
        self.nbeOfComponents = nbeOfComponents
        self.numberOfNodes = numberOfNodes
        self.numberOfDOFs = nbeOfComponents * numberOfNodes
        self.solution = {}
        self.compressedSol = {}


    def AddSolution(self, solution, time):
        """
        Adds a solution at time time

        Parameters
        ----------
        snapshot : np.ndarray
            of size (numberOfDOFs,)
        time : float
            time of the snapshot
        """
        time = float(time)
        # if not len(snapshot.shape) == 1 or not snapshot.shape[0] == self.numberOfDOFs:#pragma: no cover
        #     raise ValueError("Provided numpy array should be a vector of length {}".format(self.numberOfDOFs), snapshot.shape)

        if time in self.solution.keys():
            print(
                "Solution at time "
                + str(time)
                + " already in solution. Replacing it anyways."
            )  # pragma: no cover

        self.solution[time] = solution

        keys = list(self.solution.keys())

        if len(keys) > 1 and keys[-1] < keys[-2]:
            self.solution = dict(sorted(self.solution.items(), key=lambda x: x[0]))



    def CompressSolution(self, CorrelationOperator, reducedOrderBasis):
        """
        Compress solution using the correlation operator between the snapshots defined by the matrix snapshotCorrelationOperator and reducedOrderBasis

        Parameters
        ----------
        CorrelationOperator : feelpp._alg.MatrixSparsedouble 
            correlation operator between the snapshots
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """
        
        ur,uc = reducedOrderBasis.createVecs()

        for time, solution in self.solution.items():

            CorrelationOperator.mult(solution.to_petsc().vec(), ur)

            reducedOrderBasis.mult(ur, uc)

            self.compressedSol[time] = uc
            
        self.compressedSol = dict(sorted(self.compressedSol.items(), key=lambda x: x[0]))


    def FeelppVecToNumpy(self, vec):
        """
        Convert Feelpp function space to numpy format 

        Parameters : 
        vec : feelpp 

        Returns
        -------
        feelpp function space format 
        """
        # numberOfNodes
        return np.array(vec.to_petsc().vec())
        
    def GetSnapshot(self, time):
        """
        Returns the snapshot at time time

        Parameters
        ----------
        time : float
            time at which the snapshot is retrieved

        Returns
        -------
        np.ndarray
            snapshot
        """
        return self.snapshots[time]


    def GetCompressedSolution(self):
        """
        Returns the compressed snapshot at time time

        Parameters
        ----------
        time : float
            time at which the compressed snapshot is retrieved

        Returns
        -------
        PETSc vector of compressed solution 
        """
        return self.compressedSol


    def GetSolutionName(self):
        """
        Returns the name of the solution

        Returns
        -------
        str
            the name of the solution field
        """
        return self.solutionName


    def GetNbeOfComponents(self):
        """
        Returns the number of components of the solution

        Returns
        -------
        int
            the number of components of the solution
        """
        return self.nbeOfComponents


    def GetNumberOfDofs(self):
        """
        Returns the number of degrees of freedom of the solution

        Returns
        -------
        int
            the number of degrees of freedom of the solution
        """
        return self.numberOfDOFs


    def GetNumberOfNodes(self):
        """
        Returns the number of nodes of the solution

        Returns
        -------
        int
            the number of degrees of nodes of the solution
        """
        return self.numberOfNodes


    def GetNumberOfSnapshots(self):
        """
        Returns the number of snapshots

        Returns
        -------
        int
            the number of snapshots (= time indices) of the solution
        """
        return len(list(self.snapshots.keys()))


    def NumpyVecToFeelpp(self, vec):
        """
        Convert numpy vector to Feelpp function space format 

        Parameters : 
        vec : numpy array 

        Returns
        -------
        feelpp function space format 
        """
        # numberOfNodes
        return 

    def RemoveSnapshot(self, time):
        """
        Removes the snapshot at time time

        Parameters
        ----------
        time : float
            time of the snapshot
        """
        time = float(time)

        if time in self.snapshots:
            del self.snapshots[time]
        else:
            print("no snapshot at time "+str(time)+" to remove")


    def RemoveSnapshots(self, timeSequence):
        """
        Removes the snapshot at times timeSequence

        Parameters
        ----------
        time : list or 1d-np.ndarray of floats
            times of the snapshot
        """
        for time in timeSequence:
            self.RemoveSnapshot(time)



    # def UncompressSnapshots(self, reducedOrderBasis):
    #     """
    #     Uncompress snapshots using reducedOrderBasis

    #     Parameters
    #     ----------
    #     reducedOrderBasis : np.ndarray
    #         of size (numberOfModes, numberOfDOFs)
    #     """

    #     if bool(self.snapshots):
    #         print("Solution already uncompressed. Replacing it anyway")  # pragma: no cover

    #     snapshots = {}

    #     for time, compressedSnapshot in self.GetCompressedSnapshots().items():
    #         snapshots[time] = np.dot(compressedSnapshot, reducedOrderBasis)

    #     self.SetSnapshots(snapshots)



    def __str__(self):
        res = "Solution \n"
        res += "Name           : " + self.solutionName + "\n"
        res += "Dimensionality : " + str(self.nbeOfComponents) + "\n"
        if len(self.compressedSol) <= 0:
            res += "Not compressed"  # pragma: no cover
        else:
            res += "Compressed"  # pragma: no cover
        return res


# if __name__ == "__main__":# pragma: no cover