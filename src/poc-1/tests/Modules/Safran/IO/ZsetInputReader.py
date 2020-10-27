# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus import GetTestDataPath

def test():

    #Meca
    folder = GetTestDataPath() + "Zset/MecaSequential/"

    inputFileName = folder + "cube.inp"

    reader = ZIR.ZsetInputReader(inputFileName)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)


    #Meca2
    inputFileName = folder + "cube2.inp"

    reader = ZIR.ZsetInputReader(inputFileName)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)


    #Thermal
    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    inputFileName = folder + "cube.inp"

    reader = ZIR.ZsetInputReader(inputFileName)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
