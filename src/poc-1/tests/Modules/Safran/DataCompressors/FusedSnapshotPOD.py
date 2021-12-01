# -*- coding: utf-8 -*-

import numpy as np
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD



def test():

    numberOfNodes = 20
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.random.rand(nbeOfComponents * numberOfNodes)
    print(snapshot2)

    snapshot2 = np.array([0.53710304,0.12410915,0.57743758,0.32419659,
    0.07850115,0.73825506,0.11715959,0.31978619,0.50376855,0.11819394,
    0.1000928,0.33901801,0.88342145,0.32623183,0.8661755,0.00284833,
    0.66797476,0.37664201,0.61973928,0.4627453, 0.41163785,0.0526183,
    0.1818517, 0.79704917,0.89963221,0.51712038,0.82836401,0.77647995,
    0.11198457,0.34334608,0.72896792,0.81169613,0.23483999,0.77787556,
    0.95817958,0.77024048,0.98360743,0.55238457,0.98855662,0.22124456,
    0.89530105,0.74413058,0.29941087,0.75148103,0.89043804,0.3754997,
    0.80234039,0.25714818,0.56403225,0.09254206,0.02406722,0.54648348,
    0.19489237,0.14170761,0.38036787,0.25060818,0.74860024,0.33908417,
    0.3547198, 0.92284248])

    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.addVariabilityAxis("config", str)
    collectionProblemData.defineQuantity("U")
    collectionProblemData.AddProblemData(problemData, config="case-1")

    FusedSnapshotPOD.CompressData(
        collectionProblemData, "U", compressSolutions = True, nbModes = 5
    )

    FusedSnapshotPOD.CompressData(
        collectionProblemData, "U", 1.e-8, compressSolutions = True
    )

    FusedSnapshotPOD.CompressData(
        collectionProblemData, "U", compressSolutions = True, nbModes = 5
    )

    solution.RemoveSnapshots([0.0, 1.0])
    solution.AddSnapshot(snapshot+snapshot2, 2.0)
    solution.AddSnapshot(snapshot-snapshot2, 3.0)

    FusedSnapshotPOD.CompressData(
        collectionProblemData, "U", 1.e-8
    )

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
