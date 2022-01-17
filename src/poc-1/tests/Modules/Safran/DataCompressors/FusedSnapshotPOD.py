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
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD



def test():

    numberOfNodes = 2
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot1 = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.arange(nbeOfComponents * numberOfNodes)
    snapshot3 = np.array([0.76683505, 0.1764781,  0.71353599, 0.63196901,
    0.15739329, 0.53411207])

    solution.AddSnapshot(snapshot1, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis("config", str)
    collectionProblemData.DefineQuantity("U")
    collectionProblemData.AddProblemData(problemData, config="case-1")

    # test 1
    FusedSnapshotPOD.CompressData(collectionProblemData, "U", compressSolutions = True, nbModes = 5)

    refReducedOrderBasis = np.array(
        [[ 0.03524542,  0.16031302,  0.28538062,  0.41044822,  0.53551582,  0.66058342],
         [-0.72288815, -0.51917033, -0.3154525 , -0.11173468,  0.09198315,  0.29570098]])
    np.testing.assert_almost_equal(collectionProblemData.GetReducedOrderBasis("U"), refReducedOrderBasis)

    refCompressedSnapshots = {0.0: np.array([ 2.08748654, -1.28156153]), 1.0: np.array([7.40739933, 0.36115812])}
    for time, compSnap in refCompressedSnapshots.items():
        np.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(time), compSnap)
    #######

    # test 2
    solution.RemoveSnapshots([0.0, 1.0])
    solution.AddSnapshot(snapshot3, 2.0)
    FusedSnapshotPOD.CompressData(collectionProblemData, "U", 1.e-4, compressSolutions = True)

    refReducedOrderBasis = np.array(
    [[-0.5361379 , -0.29748055, -0.48490879, -0.43853921, -0.24363923, -0.37047027],
     [-0.54097163, -0.30385876, -0.06674588,  0.17036699,  0.40747986,  0.64459273],
     [ 0.19454937, -0.73412777,  0.24350538,  0.1751252 , -0.5577811 ,  0.1487397 ]])
    np.testing.assert_almost_equal(collectionProblemData.GetReducedOrderBasis("U"), refReducedOrderBasis)

    np.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(3.0),
                   np.array([-1.32299103e+00, 3.33066907e-16, 2.95706015e-01]))
    #######

    # test 3
    FusedSnapshotPOD.CompressData(collectionProblemData, "U", compressSolutions = True, nbModes = 1)

    refReducedOrderBasis = np.array(
    [[-0.56566467, -0.1301811 , -0.52634801, -0.46617919, -0.11610297, -0.3939939 ]])
    np.testing.assert_almost_equal(collectionProblemData.GetReducedOrderBasis("U"), refReducedOrderBasis)

    np.testing.assert_almost_equal(solution.GetCompressedSnapshotsAtTime(3.0),
                   np.array([-1.35563539e+00,]))

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
