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

    numberOfSnapshots = 0
    for s in snapshotsIterator:
        numberOfSnapshots += 1
    numberOfDOFs = s.shape[0]

    correlationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    for i, snapshot1 in enumerate(snapshotsIterator):
        matVecProduct = snapshotCorrelationOperator.dot(snapshot1)
        for j, snapshot2 in enumerate(snapshotsIterator):
            if i >= j:
                correlationMatrix[i, j] = np.dot(matVecProduct, snapshot2)
                
    mpiReducedCorrelationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))
    MPI.COMM_WORLD.Allreduce([correlationMatrix,  MPI.DOUBLE], [mpiReducedCorrelationMatrix,  MPI.DOUBLE])                

    from Mordicus.Core.BasicAlgorithms import SVD as SVD

    eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(mpiReducedCorrelationMatrix, tolerance)
    
    nbePODModes = eigenValuesRed.shape[0]
        
    reducedOrderBasis = np.zeros((nbePODModes, numberOfDOFs))
    for i in range(nbePODModes):
        for j, snapshot in enumerate(snapshotsIterator):
            reducedOrderBasis[i, :] += (eigenVectorsRed[j, i] / np.sqrt(eigenValuesRed[i])) * snapshot 

    return reducedOrderBasis


def CompressSolutionsOfCollectionProblemData(collectionProblemData, solutionName):
    """
    Compress solutions of name "solutionName" from all ProblemDatas in collectionProblemData, and update to corresponding solution.compressedSnapshots in the format ModesAndCoefficients.
        
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        input collectionProblemData containing the solutions
    solutionName : str
        name of the solutions to compress
    """
    assert isinstance(solutionName, str)

    snapshotCorrelationOperator = collectionProblemData.GetSnapshotCorrelationOperator(solutionName)
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis(solutionName)

    for _, problemData in collectionProblemData.problemDatas.items():

        if solutionName not in problemData.solutions:
            raise (
                "You must provide solutions "
                + solutionName
                + "before trying to compress them"
            )  # pragma: no cover

        solution = problemData.solutions[solutionName]

        compressedSnapshots = CompressSolutions(
            solution, snapshotCorrelationOperator, reducedOrderBasis
        )

        solution.SetCompressedSnapshots(compressedSnapshots)


def CompressSolutions(solution, snapshotCorrelationOperator, reducedOrderBasis):
    """
    Compress "solution" using the correlation operator between the snapshots defined by the matrix snapshotCorrelationOperator and "reducedOrderBasis"
        
    Parameters
    ----------
    solution : Solution
        input solution to compress
    snapshotCorrelationOperator : scipy.sparse.csr
        correlation operator between the snapshots
    reducedOrderBasis : np.ndarray
        of size (numberOfModes, numberOfDOFs)
        
    Returns
    -------
    collections.OrderedDict
        obtained compressed solution
    """

    if solution.compressedSnapshots == False:
        print("Solution already compressed. Replacing it anyway")  # pragma: no cover
        
    import collections
    compressedSnapshots = collections.OrderedDict()
    
    numberOfModes = reducedOrderBasis.shape[0]
    
    for time, snapshot in solution.snapshots.items():
        matVecProduct = snapshotCorrelationOperator.dot(snapshot)

        localScalarProduct = np.dot(reducedOrderBasis, matVecProduct)
        globalScalarProduct = np.zeros(numberOfModes)
        MPI.COMM_WORLD.Allreduce([localScalarProduct, MPI.DOUBLE], [globalScalarProduct, MPI.DOUBLE])
        
        compressedSnapshots[time] = globalScalarProduct
        
    return compressedSnapshots

