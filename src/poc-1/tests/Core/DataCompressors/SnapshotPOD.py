# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD


def test():

    numberOfNodes = 6
    nbeOfComponents = 1

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.arange(nbeOfComponents * numberOfNodes)
    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis("config", str)
    collectionProblemData.DefineQuantity("U")
    collectionProblemData.AddProblemData(problemData, config="case-1")

    reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.e-8
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    collectionProblemData.CompressSolutions("U")

    np.testing.assert_almost_equal(reducedOrdrBasis, np.array([[ 0.03524542, 0.16031302, 0.28538062, 0.41044822, 0.53551582, 0.66058342], [-0.72288815, -0.51917033, -0.3154525, -0.11173468, 0.09198315, 0.29570098]]))
    np.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(0.), np.array([ 2.08748654, -1.28156153]))
    np.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(1.), np.array([7.40739933, 0.36115812]))

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover



