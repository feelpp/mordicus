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


#REMARK: do not work very well for low values of tolerance


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


    if previousReducedOrderBasis is None:

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


        localGamma = np.dot(reducedOrderBasis, snapshotCorrelationOperator.dot(snapshots.T))
        globalGamma = np.zeros(localGamma.shape)
        MPI.COMM_WORLD.Allreduce([localGamma, MPI.DOUBLE], [globalGamma, MPI.DOUBLE])

        collectionProblemData.SetDataCompressionData(solutionName, globalGamma)



    else:

        for snap in snapshots:

            snap.shape = (1,snap.shape[0])

            gammaNPrevInd = collectionProblemData.GetDataCompressionData(solutionName)

            localGammaNNewInd = np.dot(previousReducedOrderBasis, snapshotCorrelationOperator.dot(snap.T))
            gammaNNewInd = np.zeros(localGammaNNewInd.shape)
            MPI.COMM_WORLD.Allreduce([localGammaNNewInd, MPI.DOUBLE], [gammaNNewInd, MPI.DOUBLE])

            snap = snap - np.einsum('kl,km->ml', previousReducedOrderBasis, gammaNNewInd, optimize = True)

            localNorms = np.einsum('kl,lk->k', snap, snapshotCorrelationOperator.dot(snap.T), optimize = True)
            globalNorms = np.zeros(localNorms.shape)
            MPI.COMM_WORLD.Allreduce([localNorms, MPI.DOUBLE], [globalNorms, MPI.DOUBLE])
            globalNorms = np.sqrt(globalNorms)

            snap = np.divide(snap, globalNorms[:,np.newaxis])

            indices = globalNorms > tolerance

            snap = snap[indices,:]
            globalNorms = globalNorms[indices]
            gammaNNewInd = gammaNNewInd[:,indices]

            Vinter = np.append(previousReducedOrderBasis, snap, axis=0)

            numberOfAddedSnapshots = snap.shape[0]

            gammaInterPrevInd1 = np.append(gammaNPrevInd, np.zeros((numberOfAddedSnapshots,gammaNPrevInd.shape[1])), axis = 0)

            gammaInterPrevInd2 =  np.append(gammaNNewInd, np.diag(globalNorms), axis = 0)

            gammaInterLocal = np.append(gammaInterPrevInd1, gammaInterPrevInd2, axis = 1)

            gammaInterLocal2 = np.dot(gammaInterLocal, gammaInterLocal.T)
            gammaInterGlobal2 = np.zeros(gammaInterLocal2.shape)
            MPI.COMM_WORLD.Allreduce([gammaInterLocal2, MPI.DOUBLE], [gammaInterGlobal2, MPI.DOUBLE])

            eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(gammaInterGlobal2, tolerance)

            previousReducedOrderBasis = np.dot(Vinter.T, eigenVectorsRed).T
            gammaNPrevInd = np.dot(eigenVectorsRed.T, gammaInterLocal)

        collectionProblemData.AddReducedOrderBasis(solutionName, previousReducedOrderBasis)
        collectionProblemData.SetDataCompressionData(solutionName, gammaNPrevInd)

    if compressSolutions == True:
        collectionProblemData.CompressSolutions(solutionName, snapshotCorrelationOperator)


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
