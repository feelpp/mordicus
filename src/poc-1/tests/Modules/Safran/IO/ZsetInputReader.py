# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Core import GetTestDataPath


def test():

    folder = GetTestDataPath() + "Zset/"

    inputFileName = folder + "cube.inp"

    reader = ZIR.ZsetInputReader(inputFileName)

    inputTimeSequence = reader.ReadInputTimeSequence()
    inputTimeSequence = ZIR.ReadInputTimeSequence(inputFileName)

    loadings = reader.ConstructLoadingsList()
    loadings = ZIR.ConstructLoadingsList(inputFileName)

    matFiles = reader.ReadMaterialFiles()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
