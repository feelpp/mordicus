# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import numpy as np
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Modules.Safran.DataCompressors import IncrementalSnapshotPOD



def test():

    numberOfNodes = 3
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.array([0.72257226, 0.35984262, 0.46954527, 0.23437746,
          0.13343078, 0.95540751, 0.75437321, 0.01090625, 0.1056332])

    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)


    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis("config", str)
    collectionProblemData.DefineQuantity("U")
    collectionProblemData.AddProblemData(problemData, config="case-1")

    # test 1
    IncrementalSnapshotPOD.CompressData(collectionProblemData, "U", 1.e-8, compressSolutions = True)

    refReducedOrderBasis = np.array(
    [[-0.36967,    -0.32387028, -0.33772178, -0.30802853, -0.29528259,
      -0.39906873, -0.37368532, -0.27981214, -0.29177276],
     [-0.28504611,  0.09918556, -0.01702009,  0.23208809,  0.33901873,
      -0.53168346, -0.31873217,  0.46880632,  0.36846411]])
    np.testing.assert_almost_equal(collectionProblemData.GetReducedOrderBasis("U"), refReducedOrderBasis)

    refCompressedSnapshots = {0.0: np.array([-2.97891213,  0.35508098]),
                              1.0: np.array([-1.35087006, -0.7830176 ])}
    for time, compSnap in refCompressedSnapshots.items():
        np.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(time), compSnap)
    #######

    # test 2
    solution.RemoveSnapshots([0.0, 1.0])
    solution.AddSnapshot(snapshot+snapshot2, 2.0)
    solution.AddSnapshot(snapshot-snapshot2, 3.0)

    IncrementalSnapshotPOD.CompressData(collectionProblemData, "U", 1.e-8)

    np.testing.assert_almost_equal(collectionProblemData.GetReducedOrderBasis("U"), refReducedOrderBasis)
    #######

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
