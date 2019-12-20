# -*- coding: utf-8 -*-

import numpy as np
from scipy import sparse
from MordicusCore.Containers import ProblemData
from MordicusCore.Containers import Solution
from MordicusCore.Containers import CollectionProblemData as CPD


def test():

    solution = Solution.Solution("U", 2, 10, True)
    snapshot = np.ones(20)
    snapshot2 = np.ones(20)
    solution.AddSnapshot(0., snapshot)
    solution.AddSnapshot(1., snapshot2)
    
    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)

    reducedOrderBases = np.ones((2, 20))

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)
    collectionProblemData.GetProblemData("computation1")
    collectionProblemData.GetProblemDatas()
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBases)
    collectionProblemData.GetReducedOrderBasis("U")
    collectionProblemData.GetNumberOfProblemDatas()
    collectionProblemData.GetSolutionsNumberOfDofs("U")
    collectionProblemData.GetProblemDatasTags()
    collectionProblemData.GetGlobalNumberOfSnapshots("U")
    collectionProblemData.GetSolutionsNumberOfComponents("U")
    collectionProblemData.SnapshotsIterator("U")
    collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    collectionProblemData.GetL2ScalarProducMatrix("U")
    collectionProblemData.SetL2ScalarProducMatrix("U", sparse.eye(20))
    collectionProblemData.GetL2ScalarProducMatrix("U")
    
    problemData.AddParameter(np.zeros(2), 0.)
    collectionProblemData.GetParameterDimension()
    print(collectionProblemData)

    return "ok"



if __name__ == '__main__':
    print(test()) #pragma: no cover
