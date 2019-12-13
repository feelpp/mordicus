# -*- coding: utf-8 -*-

import numpy as np
from MordicusCore.Containers.CompressedFormats import CompressedFormatsBase
from MordicusCore.Containers import Solution



def test():

    solution = Solution.Solution("U", 2, 10, True)
    snapshot1 = np.ones(20)
    snapshot2 = np.ones(20)
    compressedSnapshots = CompressedFormatsBase.CompressedFormatsBase("U")
    solution.AddSnapshot(0., snapshot1)
    solution.AddSnapshot(1., snapshot2)
    solution.GetSnapshot(1.)
    solution.GetPrimality()
    solution.GetTimeSequence()
    solution.GetSnapshotsList()
    solution.GetNbeOfComponents()
    solution.GetSolutionName()
    solution.GetNumberOfDofs()
    solution.GetNumberOfSnapshots()
    solution.GetSolutionAtTime(0.5)
    solution.SetCompressedSnapshots(compressedSnapshots)
    solution.GetCompressedSnapshots()
    print(solution)
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
