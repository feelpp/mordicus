# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core import GetTestDataPath


def test():

    folder = GetTestDataPath() + "Zset/"

    solutionFileName = folder + "cube.ut"

    reader = ZSR.ZsetSolutionReader(solutionFileName)

    snapshot = reader.ReadSnapshot("U1", 0.0, primality=True)
    snapshot = ZSR.ReadSnapshot(solutionFileName, "U1", 0.0, primality=True)

    outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()
    outputTimeSequence = ZSR.ReadTimeSequenceFromSolutionFile(solutionFileName)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
