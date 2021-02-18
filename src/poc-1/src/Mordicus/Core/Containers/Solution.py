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
        for attr, typ in zip(["solutionName", "nbeOfComponents", "numberOfNodes"], [str, int, int]):
            if not isinstance(locals()[attr], typ):
                raise TypeError("Attribute {0} should be of type {1}".format(attr, str(typ)))

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
        snapshot : np.ndarray
            of size (numberOfDOFs,)
        time : float
            time of the snapshot
        """
        time = float(time)
        if not len(snapshot.shape) == 1 or not snapshot.shape[0] == self.numberOfDOFs:
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
            self.snapshots = collections.OrderedDict(sorted(self.snapshots.items(), key=lambda x: x[0]))



    def RemoveSnapshot(self, time):
        """
        Removes the snapshot at time "time"

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
        Removes the snapshot at times "timeSequence"

        Parameters
        ----------
        time : list or 1d-np.ndarray of floats
            times of the snapshot
        """
        for time in timeSequence:
            self.RemoveSnapshot(time)


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
            snapshot at time, of size (numberOfDOFs), using PieceWiseLinearInterpolation
        """
        time = float(time)

        timeSequenceFromSnapshots = self.GetTimeSequenceFromSnapshots()
        if not timeSequenceFromSnapshots:
            raise RuntimeError("Snapshots for solutionName "+self.solutionName+" not initialized")

        return TI.PieceWiseLinearInterpolation(
            time, self.GetTimeSequenceFromSnapshots(), self.GetSnapshotsList()
        )


    def SetCompressedSnapshots(self, compressedSnapshots):
        """
        Sets the compressed representation of the solution

        Parameters
        ----------
        compressedSnapshots : collections.OrderedDict()
        """
        if not isinstance(compressedSnapshots, collections.OrderedDict):
            raise TypeError("compressedSnapshots should be an instance of OrderedDict")

        self.compressedSnapshots = compressedSnapshots


    def SetSnapshots(self, snapshots):
        """
        Sets the snapshots of the solution

        Parameters
        ----------
        snapshots : collections.OrderedDict()
        """
        if not isinstance(snapshots, collections.OrderedDict):
            raise TypeError("snapshots should be an instance of OrderedDict")

        self.snapshots = snapshots


    def AddCompressedSnapshots(self, compressedSnapshot, time):
        """
        Adds a compressed snapshot at time "time"

        Parameters
        ----------
        compressedSnapshot : np.ndarray
            of size (numberOfModes,)
        time : float
            time of the compressedSnapshot
        """
        time = float(time)
        if not len(compressedSnapshot.shape) == 1:
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
            self.compressedSnapshots = collections.OrderedDict(sorted(self.compressedSnapshots.items(), key=lambda x: x[0]))


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

        self.compressedSnapshots = collections.OrderedDict(sorted(self.compressedSnapshots.items(), key=lambda x: x[0]))



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

        import collections
        snapshots = collections.OrderedDict()

        for time, compressedSnapshot in self.compressedSnapshots.items():
            snapshots[time] = np.dot(compressedSnapshot, reducedOrderBasis)

        self.SetSnapshots(snapshots)



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



    def GetCompressedSnapshotsAtTimes(self, times):
        """
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



    def __getstate__(self):

        state = {}
        state["solutionName"] = self.solutionName
        state["nbeOfComponents"] = self.nbeOfComponents
        state["numberOfNodes"] = self.numberOfNodes
        state["numberOfDOFs"] = self.numberOfDOFs
        state["primality"] = self.primality
        state["compressedSnapshots"] = self.compressedSnapshots
        state["snapshots"] = collections.OrderedDict()

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


