# -*- coding: utf-8 -*-

import numpy as np
from Mordicus.Core.BasicAlgorithms import TimeInterpolation as TI
import collections
from mpi4py import MPI


class Solution(object):
    """
    Class containing a solution

    Attributes
    ----------
    solutionName : str
        name of the solution field (e.g. "U", "T")
    nbeOfComponents : int
        number of components of the solution (e.g. 3 for "U" in 3D, or 1 for "T")
    numberOfNodes : int
        number of nodes for the geometrical support of the solution
    numberOfDOFs : int
        number of degrees of freedom = numberOfNodes * nbeOfComponents
    primality : bool
        True for a primal solution and False for a dual solution 
    snapshots : collections.OrderedDict
        dictionary with time indices as keys and a np.ndarray of size (numberOfDOFs,) containing the solution data
    compressedSnapshots : collections.OrderedDict
        dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """

    def __init__(self, solutionName, nbeOfComponents, numberOfNodes, primality):
        """
        Parameters
        ----------
        solutionName : str
        nbeOfComponents : int
        numberOfNodes : int
        primality : np.bool
        """
        assert isinstance(solutionName, str)
        assert isinstance(nbeOfComponents, int)
        assert isinstance(numberOfNodes, int)

        self.solutionName = solutionName
        self.nbeOfComponents = nbeOfComponents
        self.numberOfNodes = numberOfNodes
        self.numberOfDOFs = nbeOfComponents * numberOfNodes
        self.primality = primality
        self.snapshots = collections.OrderedDict()
        self.compressedSnapshots = collections.OrderedDict()


    def AddSnapshot(self, snapshot, time):
        """
        Adds a snapshot at time "time"
        
        Parameters
        ----------
        time : float
            time of the snapshot
        snapshot : np.ndarray
            of size (numberOfDOFs,)
        """
        assert isinstance(time, (float, np.float64))
        assert len(snapshot.shape) == 1 and snapshot.shape[0] == self.numberOfDOFs

        if time in self.snapshots:
            print(
                "Snapshot at time "
                + str(time)
                + " already in snapshots. Replacing it anyways."
            )  # pragma: no cover
        self.snapshots[time] = snapshot
            

    def GetSnapshot(self, time):
        """
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

    def GetTimeSequenceFromSnapshots(self):
        """
        Returns
        -------
        list
            list containing the time indices of the snapshots
        """
        return list(self.snapshots.keys())

    def GetTimeSequenceFromCompressedSnapshots(self):
        """
        Returns
        -------
        list
            list containing the time indices of the compressed snapshots
        """
        return list(self.compressedSnapshots.keys())


    def GetSnapshotsList(self):
        """
        Returns
        -------
        list
            list containing the snapshots of the solution
        """
        return list(self.snapshots.values())

    def GetSolutionName(self):
        """
        Returns
        -------
        str
            the name of the solution field
        """
        return self.solutionName

    def GetNbeOfComponents(self):
        """
        Returns
        -------
        int
            the number of components of the solution
        """
        return self.nbeOfComponents

    def GetNumberOfDofs(self):
        """
        Returns
        -------
        int
            the number of degrees of freedom of the solution
        """
        return self.numberOfDOFs

    def GetNumberOfNodes(self):
        """
        Returns
        -------
        int
            the number of degrees of nodes of the solution
        """
        return self.numberOfNodes

    def GetPrimality(self):
        """
        Returns
        -------
        bool
            the primality of the solution
        """
        return self.primality

    def GetCompressedSnapshots(self):
        """
        Returns
        -------
        collections.OrderedDict
            the compressed representation of the solution
        """
        return self.compressedSnapshots

    def GetCompressedSnapshotsList(self):
        """
        Returns
        -------
        list
            list containing the snapshots of the solution
        """
        return list(self.compressedSnapshots.values())


    def GetNumberOfSnapshots(self):
        """
        Returns
        -------
        int
            the number of snapshots (= time indices) of the solution
        """
        return len(list(self.snapshots.keys()))


    def GetSnapshotAtTime(self, time):
        """
        Parameters
        ----------
        time : float
            time at which the snapshot is retrieved
            
        Returns
        -------
        np.ndarray
            snapshot at time, of size (numberOfDOFs), using TimeInterpolation
        """
        # assert type of time
        assert isinstance(time, (np.float64, float))

        return TI.TimeInterpolation(
            time, self.GetTimeSequenceFromSnapshots(), self.GetSnapshotsList()
        )


    def SetCompressedSnapshots(self, compressedSnapshots):
        """
        Sets the compressed representation of the solution
        
        Parameters
        ----------
        compressedSnapshots : collections.OrderedDict()
        """
        # assert type of compressedSnapshots
        assert isinstance(compressedSnapshots, collections.OrderedDict)

        self.compressedSnapshots = compressedSnapshots
        return
    
    
    def CompressSnapshots(self, snapshotCorrelationOperator, reducedOrderBasis):
        """
        Compress solution using the correlation operator between the snapshots defined by the matrix snapshotCorrelationOperator and "reducedOrderBasis"
            
        Parameters
        ----------
        snapshotCorrelationOperator : scipy.sparse.csr
            correlation operator between the snapshots
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """

        if self.compressedSnapshots == False:
            print("Solution already compressed. Replacing it anyway")  # pragma: no cover
            
        import collections
        compressedSnapshots = collections.OrderedDict()
        
        numberOfModes = reducedOrderBasis.shape[0]
        nNodes = self.GetNumberOfNodes()

        for time, snapshot in self.snapshots.items():
            
            matVecProduct = snapshotCorrelationOperator.dot(snapshot)

            localScalarProduct = np.dot(reducedOrderBasis, matVecProduct)
            globalScalarProduct = np.zeros(numberOfModes)
            MPI.COMM_WORLD.Allreduce([localScalarProduct, MPI.DOUBLE], [globalScalarProduct, MPI.DOUBLE])
            
            compressedSnapshots[time] = globalScalarProduct
            
        self.SetCompressedSnapshots(compressedSnapshots)
    

    def GetCompressedSnapshotsAtTime(self, time):
        """
        Parameters
        ----------
        time : float
            time at which the snapshot is retrieved
            
        Returns
        -------
        np.ndarray
            compressedSnapshots value at time, of size (numberOfModes), using TimeInterpolation
        """
        # assert type of time
        assert isinstance(time, (np.float64, float))

        return TI.TimeInterpolation(
            time, self.GetTimeSequenceFromCompressedSnapshots(), self.GetCompressedSnapshotsList()
        )    


    def __getstate__(self):
        
        state = {}
        state["solutionName"] = self.solutionName
        state["nbeOfComponents"] = self.nbeOfComponents
        state["numberOfNodes"] = self.numberOfNodes
        state["numberOfDOFs"] = self.numberOfDOFs
        state["primality"] = self.primality
        state["compressedSnapshots"] = self.compressedSnapshots
        state["snapshots"] = collections.OrderedDict()
        for time in self.GetTimeSequenceFromSnapshots():
            state["snapshots"][time] = None
            
        return state
    

    def __str__(self):
        res = "Solution \n"
        res += "Name           : " + self.solutionName + "\n"
        res += "Dimensionality : " + str(self.nbeOfComponents) + "\n"
        if self.compressedSnapshots == False:
            res += "Not compressed"  # pragma: no cover
        else:
            res += "Compressed"  # pragma: no cover
        return res
