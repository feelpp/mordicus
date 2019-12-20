# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.Containers import ProblemData
from MordicusCore.Containers import CollectionProblemData
from MordicusCore.Containers import Solution
from MordicusCore.DataCompressors import SnapshotPOD



def test():
    
    numberOfNodes = 20
    nbeOfComponents = 3
    
    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents*numberOfNodes)
    snapshot2 = np.ones(nbeOfComponents*numberOfNodes)
    solution.AddSnapshot(0., snapshot)
    solution.AddSnapshot(1., snapshot2)
    
    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)
    
    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)
    
    reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-8)
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")
    
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
