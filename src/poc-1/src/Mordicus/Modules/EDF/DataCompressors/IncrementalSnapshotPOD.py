# -*- coding: utf-8 -*-
import numpy as np
import scipy
import scipy.sparse
from Mordicus.Core.DataCompressors.SnapshotPOD import ComputeReducedOrderBasis

def CompressData(collectionProblemData, quantity, tolerance, snapshots, gram_schmidt="classical"):
    """
    Incremental POD. Note that the existing basis has to be orthonormal.

    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        input collectionProblemData containing the data
    quantity : str
        key of the physical quantity the snapshots are refferring to
    tol : float
        tolerance for the incremental SVD
    snapshots : solution
        snapshots to add to those of collectionProblemData to do the incremental POD
    
    Returns
    -------
    np.ndarray
        of size (numberOfModes, numberOfDOFs)
    """
    # TODO: allow a real snapshotCorrelationOperator

    # Get existing basis V
    basisV = collectionProblemData.GetReducedOrderBasis(quantity)
    projectedS = np.zeros((snapshots.GetNumberOfDofs(), snapshots.GetNumberOfSnapshots()))
    ai = np.zeros(snapshots.GetNumberOfDofs())
    proja = np.zeros(snapshots.GetNumberOfDofs())

    # Projects snapshots onto the orthogonal of V
    # Use "twice is enough" projection of Kahan and Parlett
    N = snapshots.GetNumberOfSnapshots()

    # TODO: it s a pity that there is not a GetNumberOfModes method
    M = basisV.shape[0]

    for i in range(N):
        proja[:] = snapshots.GetSnapshotsList()[i]
        for kp in range(2): # Kahan-Parlett process
            if gram_schmidt == "classical":
                ai[:] = proja[:]
                for k in range(M):
                    proja[:] = proja[:] - np.dot(ai,basisV[k,:])*basisV[k,:]
            if gram_schmidt == "modified":
                for k in range(M):
                    proja[:] = proja[:] - np.dot(proja,basisV[k,:])*basisV[k,:]
        projectedS[i,:] = proja[:]

    # Make a snapshot iterator out of projectedS
    snapshotsIterator = iter(projectedS[:,i] for i in range(projectedS.shape[1]))
    snapshotCorrelationOperator = scipy.sparse.identity(snapshots.GetNumberOfDofs(), format="csr")

    # Make a POD of them, call classical POD from core
    basisW = ComputeReducedOrderBasis(snapshotsIterator, snapshotCorrelationOperator, tolerance)
    
    # Concatenate both
    return np.concatenate((basisV, basisW), axis=0)
    
    