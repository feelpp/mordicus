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

from scipy import sparse
from mpi4py import MPI
from Mordicus.Core.BasicAlgorithms import SVD as SVD



def CompressData(
    collectionProblemData, solutionName, tolerance = None, snapshotCorrelationOperator = None, snapshots = None, compressSolutions = False, nbModes = None
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

    if tolerance == None and nbModes == None:# pragma: no cover
        raise("must specify epsilon or nbModes")

    if tolerance != None and nbModes != None:# pragma: no cover
        raise("cannot specify both epsilon and nbModes")

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

    if tolerance != None:
        eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)
    else:
        eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, nbModes = nbModes)

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

        if tolerance != None:
            eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)
        else:
            eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, nbModes = nbModes)

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
