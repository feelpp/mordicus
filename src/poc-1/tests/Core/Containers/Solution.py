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
    solution.AddSnapshot(0.0, snapshot1)
    solution.AddSnapshot(1.0, snapshot2)
    solution.GetSnapshot(1.0)
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
    print(solution)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
