# -*- coding: utf-8 -*-
import numpy as np


def ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, solutionName, tolerance):
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
    assert isinstance(solutionName,str)

    snapshotsIterator = collectionProblemData.SnapshotsIterator(solutionName)
    l2ScalarProducMatrix = collectionProblemData.GetL2ScalarProducMatrix(solutionName)

    return ComputeReducedOrderBasis(snapshotsIterator, l2ScalarProducMatrix, tolerance)


def ComputeReducedOrderBasis(snapshotsIterator, l2ScalarProducMatrix, tolerance):    
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the snapshots contained in the iterator  snapshotsIterator, which a correlation operator between the snapshots defined by the matrix l2ScalarProducMatrix, with tolerance as target accuracy of the data compression
    
    Parameters
    ----------
    snapshotsIterator : iterator
        iterator over the snapshots on which we want to compute a reducedOrderBasis
    l2ScalarProducMatrix : scipy.sparse.csr
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

    correlationMatrix = np.zeros((numberOfSnapshots,numberOfSnapshots))    
    for i, snapshot1 in enumerate(snapshotsIterator):
        matVecProduct = l2ScalarProducMatrix.dot(snapshot1)
        for j, snapshot2 in enumerate(snapshotsIterator):
            if i>=j:
                correlationMatrix[i,j] = np.dot(matVecProduct,snapshot2)
    
    from genericROM.BasicAlgorithms import SVD as SVD    
    eigenValuesRed, eigenVectorsRed = SVD.TruncatedSVDSymLower(correlationMatrix, tolerance)
    
    nbePODModes = eigenValuesRed.shape[0]
        
    reducedOrderBasis = np.zeros((nbePODModes, numberOfDOFs))
    for i in range(nbePODModes):
        for j, snapshot in enumerate(snapshotsIterator):
            reducedOrderBasis[i,:] += (eigenVectorsRed[j,i]/np.sqrt(eigenValuesRed[i]))*snapshot

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
    assert isinstance(solutionName,str)
    
    from genericROM.Containers.CompressedFormats import ModesAndCoefficients as MAC
    
    l2ScalarProducMatrix = collectionProblemData.GetL2ScalarProducMatrix(solutionName)
    reducedOrderBasis    = collectionProblemData.GetReducedOrderBasis(solutionName)
    
    for _, problemData in collectionProblemData.problemDatas.items():
        
        
        if solutionName not in problemData.solutions:
            raise("You must provide solutions "+solutionName+ "before trying to compress them") #pragma: no cover
        
        
        solution = problemData.solutions[solutionName]
        
        compressedSnapshotsMAC = CompressSolutions(solution, l2ScalarProducMatrix, reducedOrderBasis)
        
        solution.SetCompressedSnapshots(compressedSnapshotsMAC)    
    

    
def CompressSolutions(solution, l2ScalarProducMatrix, reducedOrderBasis):
    """
    Compress "solution" using the correlation operator between the snapshots defined by the matrix l2ScalarProducMatrix and "reducedOrderBasis"
        
    Parameters
    ----------
    solution : Solution
        input solution to compress
    l2ScalarProducMatrix : scipy.sparse.csr
        correlation operator between the snapshots
    reducedOrderBasis : np.ndarray
        of size (numberOfModes, numberOfDOFs)
        
    Returns
    -------
    ModesAndCoefficients
        obtained compressed solution
    """

    if solution.compressedSnapshots is not None:
        print("Solution already compressed. Replacing it anyway") #pragma: no cover

    
    nbePODModes = reducedOrderBasis.shape[0]
    numberOfSnapshots = solution.GetNumberOfSnapshots() 

    coefficients = np.zeros((numberOfSnapshots,nbePODModes))
    times = np.zeros(numberOfSnapshots)
    index = 0

    for time, snapshot in solution.snapshots.items():
        matVecProduct = l2ScalarProducMatrix.dot(snapshot)
        for j in range(nbePODModes):
            coefficients[index,j] = np.dot(reducedOrderBasis[j,:], matVecProduct)
        times[index] = time
        index += 1
     
    solutionName = solution.GetSolutionName()
    from genericROM.Containers.CompressedFormats import ModesAndCoefficients as MAC    
    compressedSnapshotsMAC = MAC.ModesAndCoefficients(solutionName, times, solution.GetNbeOfComponents(), solution.GetPrimality())
    compressedSnapshotsMAC.SetModes(reducedOrderBasis)
    compressedSnapshotsMAC.SetCoefficients(coefficients)
    
    return compressedSnapshotsMAC



def CheckIntegrity():
    
    
    from BasicTools.Containers.UnstructuredMeshTools import CreateCube
    from genericROM.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
    from genericROM.Containers import ProblemData
    from genericROM.Containers import CollectionProblemData
    from genericROM.Containers import Solution
    
    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3,4,3],spacing=[2.,2.,2.],ofTetras=True))
    
    nbeOfComponents = 3
    
    solution = Solution.Solution("U", nbeOfComponents, mesh.GetNumberOfNodes(), True)
    snapshot = np.ones(nbeOfComponents*mesh.GetNumberOfNodes())
    snapshot2 = np.ones(nbeOfComponents*mesh.GetNumberOfNodes())
    solution.AddSnapshot(0., snapshot)
    solution.AddSnapshot(1., snapshot2)
    
    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)
    
    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)
    
    reducedOrdrBasis = ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-8)
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")
    
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
