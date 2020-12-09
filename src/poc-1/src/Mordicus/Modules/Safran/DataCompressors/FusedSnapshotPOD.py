# -*- coding: utf-8 -*-
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from scipy import sparse
from mpi4py import MPI
from Mordicus.Core.BasicAlgorithms import SVD as SVD



def CompressData(
    collectionProblemData, solutionName, tolerance, snapshotCorrelationOperator = None, snapshots = None, compressSolutions = False
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
    compressSolutions : bool
        decides if solutions may be compressed using the constructed reducedOrderBasis

    Returns
    -------
    np.ndarray
        of size (numberOfModes, numberOfDOFs)
    """
    assert isinstance(solutionName, str)

    if snapshots is None:
        snapshots = collectionProblemData.GetSnapshots(solutionName)

    if snapshotCorrelationOperator is None:
        snapshotCorrelationOperator = sparse.eye(snapshots.shape[1])


    numberOfSnapshots = snapshots.shape[0]

    previousReducedOrderBasis = collectionProblemData.GetReducedOrderBasis(solutionName)


    correlationMatrix = np.zeros((numberOfSnapshots,numberOfSnapshots))
    for i, snapshot1 in enumerate(snapshots):
        matVecProduct = snapshotCorrelationOperator.dot(snapshot1)
        for j, snapshot2 in enumerate(snapshots):
            if j <= i and j < numberOfSnapshots:
                correlationMatrix[i, j] = np.dot(matVecProduct, snapshot2)

    mpiReducedCorrelationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    MPI.COMM_WORLD.Allreduce([correlationMatrix,  MPI.DOUBLE], [mpiReducedCorrelationMatrix,  MPI.DOUBLE])

    eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)

    nbePODModes = eigenValuesRed.shape[0]

    changeOfBasisMatrix = np.zeros((nbePODModes,numberOfSnapshots))
    for j in range(nbePODModes):
        changeOfBasisMatrix[j,:] = eigenVectorsRed[:,j]/np.sqrt(eigenValuesRed[j])

    reducedOrderBasis = np.dot(changeOfBasisMatrix,snapshots)


    if previousReducedOrderBasis is None:

        collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)


    else:
        print("detecting existing POD basis")

        snapshots = np.append(previousReducedOrderBasis, reducedOrderBasis, axis=0)

        numberOfSnapshots = snapshots.shape[0]
        correlationMatrix = np.zeros((numberOfSnapshots,numberOfSnapshots))

        for i, snapshot1 in enumerate(snapshots):
            matVecProduct = snapshotCorrelationOperator.dot(snapshot1)
            for j, snapshot2 in enumerate(snapshots):
                if j <= i and j < numberOfSnapshots:
                    correlationMatrix[i, j] = np.dot(matVecProduct, snapshot2)

        mpiReducedCorrelationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
        MPI.COMM_WORLD.Allreduce([correlationMatrix,  MPI.DOUBLE], [mpiReducedCorrelationMatrix,  MPI.DOUBLE])

        eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)

        nbePODModes = eigenValuesRed.shape[0]

        changeOfBasisMatrix = np.zeros((nbePODModes,numberOfSnapshots))
        for j in range(nbePODModes):
            changeOfBasisMatrix[j,:] = eigenVectorsRed[:,j]/np.sqrt(eigenValuesRed[j])

        reducedOrderBasis = np.dot(changeOfBasisMatrix,snapshots)
        collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)


    if compressSolutions == True:
        collectionProblemData.CompressSolutions(solutionName, snapshotCorrelationOperator)


    print("POD for "+solutionName+" : number of snapshots = "+str(numberOfSnapshots)+", number of modes = "+str(nbePODModes))


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
