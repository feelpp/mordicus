# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD


def test():

    numberOfNodes = 20
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.random.rand(nbeOfComponents * numberOfNodes)
    solution.AddSnapshot(0.0, snapshot)
    solution.AddSnapshot(1.0, snapshot2)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)

    reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.e-8
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
