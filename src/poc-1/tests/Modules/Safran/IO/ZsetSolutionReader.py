# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus import GetTestDataPath, GetTestPath
from Mordicus.Core.IO import StateIO as SIO
import numpy as np
import os


def test():

    folder = GetTestDataPath() + "Zset/MecaSequential/"

    solutionFileName = folder + "cube.ut"

    reader = ZSR.ZsetSolutionReader(solutionFileName)

    ref = SIO.LoadState(GetTestPath() + os.sep + "Modules/Safran/IO/ref/ZsetSolutionReader", extension = 'res')

    snapshotComponent = reader.ReadSnapshotComponent("U1", 1.0, primality=True)
    np.testing.assert_almost_equal(snapshotComponent, ref[0])
    ZSR.ReadSnapshotComponent(solutionFileName, "U1", 1.0, primality=True)

    timeSequence = reader.ReadTimeSequenceFromSolutionFile()
    np.testing.assert_almost_equal(timeSequence, ref[1])
    ZSR.ReadTimeSequenceFromSolutionFile(solutionFileName)

    timeSequence2 = [0.0, 0.2, 0.8, 1.0, 1.4, 1.6, 2.0]
    snapshotComponentTimeSequence = reader.ReadSnapshotComponentTimeSequence("U1", timeSequence2, primality=True)
    np.testing.assert_almost_equal(snapshotComponentTimeSequence, ref[2])

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
