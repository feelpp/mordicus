# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus import GetTestDataPath


def test():

    folder = GetTestDataPath() + "Zset/MecaSequential/"

    solutionFileName = folder + "cube.ut"

    reader = ZSR.ZsetSolutionReader(solutionFileName)

    reader.ReadSnapshotComponent("U1", 0.0, primality=True)
    ZSR.ReadSnapshotComponent(solutionFileName, "U1", 0.0, primality=True)

    reader.ReadTimeSequenceFromSolutionFile()
    ZSR.ReadTimeSequenceFromSolutionFile(solutionFileName)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
