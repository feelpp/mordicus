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

from Mordicus.Core.BasicAlgorithms import Interpolation as TI
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
    snapshots : dict
        dictionary with time indices as keys and a np.ndarray of size (numberOfDOFs,) containing the solution data
    compressedSnapshots : dict
        dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    """

    def __init__(self, solutionName, nbeOfComponents, numberOfNodes, primality):

        for attr, typ in zip(["solutionName", "nbeOfComponents", "numberOfNodes"], [str, int, int]):
            if not isinstance(locals()[attr], typ):#pragma: no cover
                raise TypeError("Attribute {0} should be of type {1}".format(attr, str(typ)))

        self.solutionName = solutionName
        self.nbeOfComponents = nbeOfComponents
        self.numberOfNodes = numberOfNodes
        self.numberOfDOFs = nbeOfComponents * numberOfNodes
        self.primality = primality
        self.snapshots = {}
        self.compressedSnapshots = {}


    def AddSnapshot(self, snapshot, time):
        """
        Adds a snapshot at time time

        Parameters
        ----------
        snapshot : np.ndarray
            of size (numberOfDOFs,)
        time : float
            time of the snapshot
        """
        time = float(time)
        if not len(snapshot.shape) == 1 or not snapshot.shape[0] == self.numberOfDOFs:#pragma: no cover
            raise ValueError("Provided numpy array should be a vector of length {}".format(self.numberOfDOFs))

        if time in self.snapshots:
            print(
                "Snapshot at time "
                + str(time)
                + " already in snapshots. Replacing it anyways."
            )  # pragma: no cover

        self.snapshots[time] = snapshot

        keys = list(self.snapshots.keys())

        if len(keys) > 1 and keys[-1] < keys[-2]:
            self.snapshots = dict(sorted(self.snapshots.items(), key=lambda x: x[0]))


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


    def GetCompressedSnapshot(self, time):
        """
        Returns the compressed snapshot at time time

        Parameters
        ----------
        time : float
            time at which the compressed snapshot is retrieved

        Returns
        -------
        np.ndarray
            compressed snapshot
        """
        return self.compressedSnapshots[time]


    def GetTimeSequenceFromSnapshots(self):
        """
        Returns the time sequence from the snapshots dictionary

        Returns
        -------
        list
            list containing the time indices of the snapshots
        """
        return list(self.snapshots.keys())


    def GetTimeSequenceFromCompressedSnapshots(self):
        """
        Returns the time sequence from the compressedSnapshots dictionary

        Returns
        -------
        list
            list containing the time indices of the compressed snapshots
        """
        return list(self.compressedSnapshots.keys())


    def GetSnapshotsList(self):
        """
        Returns the snapshots in the form of a list

        Returns
        -------
        list
            list containing the snapshots of the solution
        """
        return list(self.snapshots.values())


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


    def GetPrimality(self):
        """
        Returns the primality of the solution

        Returns
        -------
        bool
            the primality of the solution
        """
        return self.primality


    def GetSnapshots(self):
        """
        Returns the complete snapshots dictionary

        Returns
        -------
        dict
            the snapshots dictionary of the solution
        """
        return self.snapshots


    def GetCompressedSnapshots(self):
        """
        Returns the complete compressedSnapshots dictionary

        Returns
        -------
        dict
            the compressed representation of the solution
        """
        return self.compressedSnapshots


    def GetCompressedSnapshotsList(self):
        """
        Returns the compressed snapshots in the form of a list

        Returns
        -------
        list
            list containing the snapshots of the solution
        """
        return list(self.compressedSnapshots.values())


    def GetNumberOfSnapshots(self):
        """
        Returns the number of snapshots

        Returns
        -------
        int
            the number of snapshots (= time indices) of the solution
        """
        return len(list(self.snapshots.keys()))


    def GetSnapshotAtTime(self, time):
        """
        Returns the snapshots at a specitiy time (with time interpolation if needed)

        Parameters
        ----------
        time : float
            time at which the snapshot is retrieved

        Returns
        -------
        np.ndarray
            snapshot at time, of size (numberOfDOFs), using PieceWiseLinearInterpolation
        """
        time = float(time)

        timeSequenceFromSnapshots = self.GetTimeSequenceFromSnapshots()
        if not timeSequenceFromSnapshots:#pragma: no cover
            raise RuntimeError("Snapshots for solutionName "+self.solutionName+" not initialized")

        return TI.PieceWiseLinearInterpolation(
            time, timeSequenceFromSnapshots, self.GetSnapshotsList()
        )


    def SetCompressedSnapshots(self, compressedSnapshots):
        """
        Sets the compressed representation of the solution

        Parameters
        ----------
        compressedSnapshots : dict
        """
        if not isinstance(compressedSnapshots, dict):#pragma: no cover
            raise TypeError("compressedSnapshots should be an instance of dict")

        self.compressedSnapshots = compressedSnapshots


    def SetSnapshots(self, snapshots):
        """
        Sets the snapshots of the solution

        Parameters
        ----------
        snapshots : dict
        """
        if not isinstance(snapshots, dict):#pragma: no cover
            raise TypeError("snapshots should be an instance of dict")
        for time, snapshot in snapshots.items():
            if not len(snapshot.shape) == 1 or not snapshot.shape[0] == self.numberOfDOFs:#pragma: no cover
                raise ValueError("Provided numpy array for time "+str(time)+" should be a vector of length {}".format(self.numberOfDOFs))

        self.snapshots = snapshots


    def AddCompressedSnapshots(self, compressedSnapshot, time):
        """
        Adds a compressed snapshot at time time

        Parameters
        ----------
        compressedSnapshot : np.ndarray
            of size (numberOfModes,)
        time : float
            time of the compressed snapshot
        """
        time = float(time)
        if not len(compressedSnapshot.shape) == 1:#pragma: no cover
            raise ValueError("compressedSnapshot should be a vector, not a multidimensional array")

        if time in self.compressedSnapshots:
            print(
                "Snapshot at time "
                + str(time)
                + " already in compressedSnapshot. Replacing it anyways."
            )  # pragma: no cover

        self.compressedSnapshots[time] = compressedSnapshot

        keys = list(self.compressedSnapshots.keys())

        if len(keys) > 1 and keys[-1] < keys[-2]:
            self.compressedSnapshots = dict(sorted(self.compressedSnapshots.items(), key=lambda x: x[0]))


    def CompressSnapshots(self, snapshotCorrelationOperator, reducedOrderBasis):
        """
        Compress snapshots using the correlation operator between the snapshots defined by the matrix snapshotCorrelationOperator and reducedOrderBasis

        Parameters
        ----------
        snapshotCorrelationOperator : scipy.sparse.csr
            correlation operator between the snapshots
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """

        numberOfModes = reducedOrderBasis.shape[0]

        for time, snapshot in self.snapshots.items():

            matVecProduct = snapshotCorrelationOperator.dot(snapshot)

            localScalarProduct = np.dot(reducedOrderBasis, matVecProduct)
            globalScalarProduct = np.zeros(numberOfModes)
            MPI.COMM_WORLD.Allreduce([localScalarProduct, MPI.DOUBLE], [globalScalarProduct, MPI.DOUBLE])

            self.compressedSnapshots[time] = globalScalarProduct

        self.compressedSnapshots = dict(sorted(self.compressedSnapshots.items(), key=lambda x: x[0]))


    def UncompressSnapshots(self, reducedOrderBasis):
        """
        Uncompress snapshots using reducedOrderBasis

        Parameters
        ----------
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """

        if bool(self.snapshots):
            print("Solution already uncompressed. Replacing it anyway")  # pragma: no cover

        snapshots = {}

        for time, compressedSnapshot in self.GetCompressedSnapshots().items():
            snapshots[time] = np.dot(compressedSnapshot, reducedOrderBasis)

        self.SetSnapshots(snapshots)


    def UncompressSnapshotAtTime(self, reducedOrderBasis, time):
        """
        Uncompress snapshot at time using reducedOrderBasis

        Parameters
        ----------
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        time : float
        """

        if time in self.snapshots:
            print("Solution already uncompressed at time "+str(time)+". Replacing it anyway")  # pragma: no cover

        self.snapshots[time] = np.dot(self.GetCompressedSnapshotsAtTime(time), reducedOrderBasis)


    def ConvertCompressedSnapshotReducedOrderBasis(self, projectedReducedOrderBasis):
        """
        Converts the reducedSnapshot from the current reducedOrderBasis to a newReducedOrderBasis using a projectedReducedOrderBasis between the current one and a new one

        Parameters
        ----------
        projectedReducedOrderBasis : np.ndarray
            of size (newNumberOfModes, numberOfModes)
        """
        for time, compressedSnapshot in self.compressedSnapshots.items():
            self.compressedSnapshots[time] = np.dot(projectedReducedOrderBasis, compressedSnapshot)


    def ConvertCompressedSnapshotReducedOrderBasisAtTime(self, projectedReducedOrderBasis, time):
        """
        Converts the reducedSnapshot at time from the current reducedOrderBasis to a newReducedOrderBasis using a projectedReducedOrderBasis between the current one and a new one

        Parameters
        ----------
        projectedReducedOrderBasis : np.ndarray
            of size (newNumberOfModes, numberOfModes)
        time : float
        """
        self.compressedSnapshots[time] = np.dot(projectedReducedOrderBasis, self.compressedSnapshots[time])


    def GetCompressedSnapshotsAtTime(self, time):
        """
        Parameters
        ----------
        time : float
            time at which the compressed snapshot is retrieved

        Returns
        -------
        np.ndarray
            compressedSnapshot value at time, of size (numberOfModes), using PieceWiseLinearInterpolation
        """
        time = float(time)

        return TI.PieceWiseLinearInterpolation(
            time, self.GetTimeSequenceFromCompressedSnapshots(), self.GetCompressedSnapshotsList()
        )
        #return self.compressedSnapshots[time]


    def GetCompressedSnapshotsAtTimes(self, times):
        """
        Returns the compressed snapshot at a specitiy time (with time interpolation if needed)

        Parameters
        ----------
        times : list or 1D ndarray of floats
            times at which the compressed snapshot are retrieved

        Returns
        -------
        np.ndarray
            compressedSnapshots values at times, of size (numberOfModes), using PieceWiseLinearInterpolationVectorized
        """

        return TI.PieceWiseLinearInterpolationVectorized(
            times, self.GetTimeSequenceFromCompressedSnapshots(), self.GetCompressedSnapshotsList()
        )

    def accept(self, visitor):
        """
        Accept visitor
        """
        return visitor.visitSolution(self)

    def __getstate__(self):

        state = {}
        state["solutionName"] = self.solutionName
        state["nbeOfComponents"] = self.nbeOfComponents
        state["numberOfNodes"] = self.numberOfNodes
        state["numberOfDOFs"] = self.numberOfDOFs
        state["primality"] = self.primality
        state["compressedSnapshots"] = self.compressedSnapshots
        state["snapshots"] = dict

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


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


