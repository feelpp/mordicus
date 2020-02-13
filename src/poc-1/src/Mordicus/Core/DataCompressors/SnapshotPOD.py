# -*- coding: utf-8 -*-
import numpy as np
from mpi4py import MPI


def ComputeReducedOrderBasisFromCollectionProblemData(
    collectionProblemData, solutionName, tolerance
):
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the snapshots contained in the solutions of name "solutionName" from all problemDatas in collectionProblemData, with tolerance as target accuracy of the data compression

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        input collectionProblemData containing the data
    solutionName : str
        name of the solutions from which snapshots are taken
    tolerance : float
        target accuracy of the data compression

    Returns
    -------
    np.ndarray
        of size (numberOfModes, numberOfDOFs)
    """
    assert isinstance(solutionName, str)

    snapshotsIterator = collectionProblemData.SnapshotsIterator(solutionName)
    snapshotCorrelationOperator = collectionProblemData.GetSnapshotCorrelationOperator(solutionName)

    return ComputeReducedOrderBasis(snapshotsIterator, snapshotCorrelationOperator, tolerance)


def ComputeReducedOrderBasis(snapshotsIterator, snapshotCorrelationOperator, tolerance):
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the snapshots contained in the iterator  snapshotsIterator, which a correlation operator between the snapshots defined by the matrix snapshotCorrelationOperator, with tolerance as target accuracy of the data compression

    Parameters
    ----------
    snapshotsIterator : iterator
        iterator over the snapshots on which we want to compute a reducedOrderBasis
    snapshotCorrelationOperator : scipy.sparse.csr
        correlation operator between the snapshots
    tolerance : float
        target accuracy of the data compression

    Returns
    -------
    np.ndarray
        of size (numberOfModes, numberOfDOFs)
    """

    snapshots = []

    for s in snapshotsIterator:
        snapshots.append(s)

    snapshots = np.array(snapshots)

    numberOfDOFs = snapshots.shape[1]
    numberOfSnapshots = snapshots.shape[0]


    correlationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    for i, snapshot1 in enumerate(snapshots):
        matVecProduct = snapshotCorrelationOperator.dot(snapshot1)
        for j, snapshot2 in enumerate(snapshots):
            if i >= j:
                correlationMatrix[i, j] = np.dot(matVecProduct, snapshot2)


    mpiReducedCorrelationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    MPI.COMM_WORLD.Allreduce([correlationMatrix,  MPI.DOUBLE], [mpiReducedCorrelationMatrix,  MPI.DOUBLE])

    from Mordicus.Core.BasicAlgorithms import SVD as SVD


    eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)

    nbePODModes = eigenValuesRed.shape[0]

    print("nbePODModes =", nbePODModes)


    changeOfBasisMatrix = np.zeros((nbePODModes,numberOfSnapshots))
    for j in range(nbePODModes):
        changeOfBasisMatrix[j,:] = eigenVectorsRed[:,j]/np.sqrt(eigenValuesRed[j])

    reducedOrderBasis = np.dot(changeOfBasisMatrix,snapshots)


    return reducedOrderBasis




