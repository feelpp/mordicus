# -*- coding: utf-8 -*-

import numpy as np
import os
from scipy import sparse
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import CollectionProblemData as CPD


def test():

    solution = Solution.Solution("U", 2, 10, True)
    snapshot = np.ones(20)
    snapshot2 = 1.+np.ones(20)
    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    reducedOrderBases = np.ones((2, 20))

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.defineVariabilityAxes(["mu1"],
                                                [float],
                                                quantities=[("name", "unit")], 
                                                descriptions=["Parameter long description"])
    collectionProblemData.addVariabilityAxis("mu2",
                                            float,
                                            quantity=("name", "unit"), 
                                            description="Parameter long description")
    collectionProblemData.AddProblemData(problemData, mu1=0., mu2=0.)
    collectionProblemData.getNumberOfVariabilityAxes()
    collectionProblemData.GetProblemData(mu1=0., mu2=0.)
    collectionProblemData.GetProblemDatas()
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBases)
    collectionProblemData.GetReducedOrderBasis("U")
    collectionProblemData.GetNumberOfProblemDatas()
    collectionProblemData.GetSolutionsNumberOfDofs("U")
    collectionProblemData.GetSolutionsNumberOfNodes("U")
    collectionProblemData.GetProblemSampling()
    collectionProblemData.GetGlobalNumberOfSnapshots("U")
    collectionProblemData.GetGlobalNumberOfSnapshots("U", skipFirst = True)
    collectionProblemData.GetSolutionsNumberOfComponents("U")
    #collectionProblemData.SnapshotsIterator("U")
    #collectionProblemData.SnapshotsIterator("U", skipFirst = True)
    for s in collectionProblemData.SnapshotsIterator("U"):
        pass
    for s in collectionProblemData.SnapshotsIterator("U", skipFirst = True):
        pass
    collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    collectionProblemData.GetSnapshotCorrelationOperator("U")
    collectionProblemData.SetSnapshotCorrelationOperator("U", sparse.eye(20))
    collectionProblemData.GetSnapshotCorrelationOperator("U")


    problemData.AddParameter(np.zeros(2), 0.0)
    collectionProblemData.GetParameterDimension()
    collectionProblemData.SaveState("temp")
    CPD.LoadState("temp")
    os.system("rm -rf temp.pkl")

    print(collectionProblemData)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
