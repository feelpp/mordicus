# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Core import GetTestDataPath
import os

def test():

    #MECA
    folder = GetTestDataPath() + "Zset/MecaSequential/"

    inputFileName = folder + "cube.inp"

    reader = ZIR.ZsetInputReader(inputFileName)

    inputTimeSequence = reader.ReadInputTimeSequence()
    inputTimeSequence = ZIR.ReadInputTimeSequence(inputFileName)

    loadings = reader.ConstructLoadingsList()
    loadings = ZIR.ConstructLoadingsList(inputFileName)

    constitutiveLaws = reader.ConstructConstitutiveLawsList()
    constitutiveLaws = ZIR.ConstructConstitutiveLawsList(inputFileName)


    #Thermal
    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    inputFileName = folder + "cube.inp"

    reader = ZIR.ZsetInputReader(inputFileName)

    inputTimeSequence = reader.ReadInputTimeSequence()
    inputTimeSequence = ZIR.ReadInputTimeSequence(inputFileName)

    loadings = reader.ConstructLoadingsList()
    loadings = ZIR.ConstructLoadingsList(inputFileName)

    constitutiveLaws = reader.ConstructConstitutiveLawsList()
    constitutiveLaws = ZIR.ConstructConstitutiveLawsList(inputFileName)


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
