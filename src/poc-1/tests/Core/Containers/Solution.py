# -*- coding: utf-8 -*-

import numpy as np
from Mordicus.Core.Containers import Solution
import collections

def test():

    solution = Solution.Solution("U", 2, 10, True)
    snapshot1 = np.ones(20)
    snapshot2 = np.ones(20)
    compressedSnapshots = collections.OrderedDict()
    compressedSnapshots[0.0] = np.ones(2)
    compressedSnapshots[1.0] = np.ones(2)
    solution.AddSnapshot(snapshot1, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)
    solution.AddSnapshot(snapshot1, 0.5)
    solution.RemoveSnapshot(0.5)
    solution.RemoveSnapshot(0.7)
    solution.AddSnapshot(snapshot1, 0.5)
    solution.RemoveSnapshots([0.5, 0.])
    solution.AddSnapshot(snapshot1, 0.0)
    solution.AddCompressedSnapshots(np.ones(2), 1.)
    solution.AddCompressedSnapshots(np.ones(2), 0.)
    solution.GetSnapshot(1.0)
    solution.ConvertCompressedSnapshotReducedOrderBasis(np.random.rand(3,2))
    solution.ConvertCompressedSnapshotReducedOrderBasisAtTime(np.random.rand(4,3), 0.)
    solution.GetPrimality()
    solution.GetTimeSequenceFromSnapshots()
    solution.GetSnapshotsList()
    solution.GetNbeOfComponents()
    solution.GetSolutionName()
    solution.GetNumberOfDofs()
    solution.GetNumberOfSnapshots()
    solution.GetSnapshotAtTime(0.5)
    solution.SetCompressedSnapshots(compressedSnapshots)
    solution.GetCompressedSnapshots()
    solution.GetCompressedSnapshotsList()
    solution.GetTimeSequenceFromCompressedSnapshots()
    solution.GetCompressedSnapshotsAtTime(0.5)
    solution.GetCompressedSnapshotsAtTimes([0.5, 0.6])
    print(solution)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
