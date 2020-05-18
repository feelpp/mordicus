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
    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.addVariabilityAxis("config", str)
    collectionProblemData.defineQuantity("U")
    collectionProblemData.AddProblemData(problemData, config="case-1")

    reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.e-8
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    collectionProblemData.CompressSolutions("U")

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
