# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

from ast import MatMult
import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from mpi4py import MPI
from scipy import sparse
from petsc4py import PETSc
import petsc4py
from petsc4py import *


def ComputeReducedOrderBasisWithPOD(snapshotList, snapshotCorrelationOperator, tolerance=1.e-6):
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the
    snapshots contained in the iterator snapshotsIterator, which a correlation
    operator between the snapshots defined by the matrix
    snapshotCorrelationOperator, with tolerance as target accuracy of the data
    compression

    Parameters
    ----------
    snapshotList : List(of feelpp.functionSpace().element())
        List  of the snapshots on which we want to compute a reducedOrderBasis
    snapshotCorrelationOperator : feelpp.algMat
        correlation operator between the snapshots
    tolerance : float
        target accuracy of the data compression

    Returns
    -------
    np.ndarray
        of size (numberOfModes, numberOfDOFs)
    """

    snapshots = []

    numberOfDofs = snapshotList[0].functionSpace().nDof() 

    for s in snapshotList:
        snapshots.append(s.to_petsc().vec()[:])

    # snapshots = np.array(snapshots)

    # numberOfSnapshots = snapshots.shape[0]
    numberOfSnapshots = len(snapshotList)
    print('number of snapshots = ', numberOfSnapshots)
    
    correlationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    for i, snapshot1 in enumerate(snapshotList):
        for j, snapshot2 in enumerate(snapshotList):
            if i >= j:
                correlationMatrix[i, j] = snapshotCorrelationOperator.energy(snapshot1, snapshot2)


    mpiReducedCorrelationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    MPI.COMM_WORLD.Allreduce([correlationMatrix,  MPI.DOUBLE], [mpiReducedCorrelationMatrix,  MPI.DOUBLE])

    from Mordicus.Core.BasicAlgorithms import SVD as SVD


    eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)

    nbePODModes = eigenValuesRed.shape[0]

    print("nbePODModes =", nbePODModes)


    changeOfBasisMatrix = np.zeros((nbePODModes,numberOfSnapshots))
    for j in range(nbePODModes):
        changeOfBasisMatrix[j,:] = eigenVectorsRed[:,j]/np.sqrt(eigenValuesRed[j])

    snapshots = np.array(snapshots)
    reducedOrderBasis = np.dot(changeOfBasisMatrix,snapshots)


    return reducedOrderBasis



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)




