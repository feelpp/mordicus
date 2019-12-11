# -*- coding: utf-8 -*-

"""
All files in this folder must implement two functions:
    - ComputeReducedOrderBasisFromCollectionProblemData:
    
    Computes a reducedOrderBasis using the proposed algorithm, from the snapshots contained in the solutions of name "solutionName" from all problemDatas in collectionProblemData, with tolerance as target accuracy of the data compression
    
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
        
        
    - CompressSolutionsOfCollectionProblemData:
    
    Compress solutions of name "solutionName" from all ProblemDatas in collectionProblemData, and update to corresponding solution.compressedSnapshots in the format ModesAndCoefficients.
        
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        input collectionProblemData containing the solutions
    solutionName : str
        name of the solutions to compress        
"""

__all__ = ["SnapshotPOD"]
