# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus import GetTestDataPath

def test():

    # with fileName
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


    #Meca Alternate Temp definition
    folder = GetTestDataPath() + "Zset/MecaAlternateTempDefinition/"

    inputFileName = folder + "cube.inp"

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


    # with string
    #Meca
    folder = GetTestDataPath() + "Zset/MecaSequential/"
    f = open(folder + "cube.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)


    #Meca2
    f = open(folder + "cube2.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)


    #Meca Alternate Temp definition
    folder = GetTestDataPath() + "Zset/MecaAlternateTempDefinition/"

    f = open(folder + "cube.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)


    #Thermal
    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    f = open(folder + "cube.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ReadInputTimeSequence()
    ZIR.ReadInputTimeSequence(inputFileName)

    reader.ConstructLoadingsList()
    ZIR.ConstructLoadingsList(inputFileName)

    reader.ConstructConstitutiveLawsList()
    ZIR.ConstructConstitutiveLawsList(inputFileName)




    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
