# -*- coding: utf-8 -*-


from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus import GetTestDataPath
import numpy as np


def test():


    timeSequenceRef1 = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    timeSequenceRef2 = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0,
    2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0,
    5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0]
    timeSequenceRef3 = [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]

    pressureRef = np.array([0.10154731, 0.13406202, 0.1674232 , 0.19778715, 0.2210309 ,
    0.23365791, 0.13406202, 0.17698772, 0.2210309 , 0.26111716, 0.29180342,
    0.3084735 , 0.1674232 , 0.2210309 , 0.2760342 , 0.32609588, 0.36441836,
    0.38523677, 0.19778715, 0.26111716, 0.32609588, 0.38523677, 0.43050942,
    0.45510346, 0.2210309 , 0.29180342, 0.36441836, 0.43050942, 0.4811025 ,
    0.5085868 , 0.23365791, 0.3084735 , 0.38523677, 0.45510346, 0.5085868 , 0.5376412 ])

    temperatureRef = np.fromfile(GetTestDataPath() + "Zset/MecaSequential/temperature2.node", dtype=np.float32).byteswap()

    # with fileName
    #Meca
    folder = GetTestDataPath() + "Zset/MecaSequential/"

    inputFileName = folder + "cube.inp"

    initialCondition = ZIR.ConstructInitialCondition(inputFileName)
    assert initialCondition.dataType == {'U': 'scalar'}
    assert initialCondition.initialSnapshot == {'U': 0.0}
    assert initialCondition.reducedInitialSnapshot == {}

    np.testing.assert_almost_equal(ZIR.ReadInputTimeSequence(inputFileName), timeSequenceRef1)

    loadingList = ZIR.ConstructLoadingsList(inputFileName)
    #loading0
    assert loadingList[0].solutionName == "U"
    assert loadingList[0].set == "x1"
    assert loadingList[0].type == "pressure"
    np.testing.assert_almost_equal(loadingList[0].coefficientsTimes, [0.,0.1,2.])
    np.testing.assert_almost_equal(loadingList[0].coefficientsValues, [0.,-100.,-100.])
    np.testing.assert_almost_equal(loadingList[0].fieldsMapTimes, [0.,0.1,2.])
    assert len(loadingList[0].fieldsMapValues) == 3
    for val in loadingList[0].fieldsMapValues:
        assert val == 'pressure.node'
    assert len(list(loadingList[0].fields.keys())) == 1
    assert 'pressure.node' in loadingList[0].fields
    np.testing.assert_almost_equal(loadingList[0].fields['pressure.node'],pressureRef)
    assert loadingList[0].assembledReducedFields == {}

    #loading1
    assert loadingList[1].solutionName == "U"
    assert loadingList[1].set == "ALL_ELEMENT"
    assert loadingList[1].type == "centrifugal"
    np.testing.assert_almost_equal(loadingList[1].rotationVelocityTimes, [0.,1.,2.])
    np.testing.assert_almost_equal(loadingList[1].rotationVelocityValues, [0.,1.,1.])
    np.testing.assert_almost_equal(loadingList[1].center, [3.5,-20.,1.5])
    np.testing.assert_almost_equal(loadingList[1].direction, [0.,0.,1.])
    assert loadingList[1].coefficient == 15000.
    assert loadingList[1].reducedUnitCentrifugalVector == None
    assert loadingList[1].reducedIntegrationWeights == None
    assert loadingList[1].reducedIntegrationPoints == None
    assert loadingList[1].reducedUnAssembledReducedUnitCentrifugalVector == None
    assert loadingList[1].JdetAtReducedIntegPoint == None

    #loading2
    assert loadingList[2].solutionName == "U"
    assert loadingList[2].set == "ALLNODE"
    assert loadingList[2].type == "temperature"
    np.testing.assert_almost_equal(loadingList[2].fieldsMapTimes, [0.,1.,2.])
    assert len(loadingList[2].fieldsMapValues) == 3
    assert loadingList[2].fieldsMapValues[0] == 'temperature1.node'
    assert loadingList[2].fieldsMapValues[1] == 'temperature2.node'
    assert loadingList[2].fieldsMapValues[2] == 'temperature1.node'
    assert loadingList[2].phiAtReducedIntegPoint == None
    assert len(list(loadingList[2].fields.keys())) == 2
    assert 'temperature1.node' in loadingList[2].fields
    assert 'temperature2.node' in loadingList[2].fields
    np.testing.assert_almost_equal(loadingList[2].fields['temperature1.node'],20.+np.zeros(343))
    np.testing.assert_almost_equal(loadingList[2].fields['temperature2.node'],temperatureRef)
    assert loadingList[2].fieldsAtReducedIntegrationPoints == {}

    constitutiveLawsList = ZIR.ConstructConstitutiveLawsList(inputFileName)
    assert constitutiveLawsList[0].set == 'ALLELEMENT'
    assert constitutiveLawsList[0].type == 'mechanical'
    assert constitutiveLawsList[0].constitutiveLawVariables['nstatv'] == 20
    assert constitutiveLawsList[0].density == 1.e-8
    assert constitutiveLawsList[0].behavior == 'gen_evp'


    #Meca2
    inputFileName = folder + "cube2.inp"

    initialCondition = ZIR.ConstructInitialCondition(inputFileName)
    assert initialCondition.dataType == {'U': 'scalar'}
    assert initialCondition.initialSnapshot == {'U': 0.0}
    assert initialCondition.reducedInitialSnapshot == {}

    np.testing.assert_almost_equal(ZIR.ReadInputTimeSequence(inputFileName), timeSequenceRef2)

    loadingList = ZIR.ConstructLoadingsList(inputFileName)
    #loading0
    assert loadingList[0].solutionName == "U"
    assert loadingList[0].set == "x1"
    assert loadingList[0].type == "pressure"
    np.testing.assert_almost_equal(loadingList[0].coefficientsTimes, [0.,0.1,2.,2.1,4.,4.1,6.,6.1,8.])
    np.testing.assert_almost_equal(loadingList[0].coefficientsValues,[0.,-100.,0.,-100.,0.,-100.,0.,-100.,0.])
    np.testing.assert_almost_equal(loadingList[0].fieldsMapTimes, [0.,0.1,2.,2.1,4.,4.1,6.,6.1,8.])
    assert len(loadingList[0].fieldsMapValues) == 9
    for val in loadingList[0].fieldsMapValues:
        assert val == 'pressure.node'
    assert len(list(loadingList[0].fields.keys())) == 1
    assert 'pressure.node' in loadingList[0].fields
    np.testing.assert_almost_equal(loadingList[0].fields['pressure.node'],pressureRef)
    assert loadingList[0].assembledReducedFields == {}

    #loading1
    assert loadingList[1].solutionName == "U"
    assert loadingList[1].set == "ALL_ELEMENT"
    assert loadingList[1].type == "centrifugal"
    np.testing.assert_almost_equal(loadingList[1].rotationVelocityTimes, [0.,0.5,1.,1.5,2.,2.5,3.,3.5,4.,4.5,5.,5.5,6.,6.5,7.,7.5,8.])
    np.testing.assert_almost_equal(loadingList[1].rotationVelocityValues, [0.,0.3,1.,0.7,0.,0.3,1.,0.7,0.,0.3,1.,0.7,0.,0.3,1.,0.7,0.])
    np.testing.assert_almost_equal(loadingList[1].center, [3.5,-20.,1.5])
    np.testing.assert_almost_equal(loadingList[1].direction, [0.,0.,1.])
    assert loadingList[1].coefficient == 100.
    assert loadingList[1].reducedUnitCentrifugalVector == None
    assert loadingList[1].reducedIntegrationWeights == None
    assert loadingList[1].reducedIntegrationPoints == None
    assert loadingList[1].reducedUnAssembledReducedUnitCentrifugalVector == None
    assert loadingList[1].JdetAtReducedIntegPoint == None

    #loading2
    assert loadingList[2].solutionName == "U"
    assert loadingList[2].set == "ALLNODE"
    assert loadingList[2].type == "temperature"
    np.testing.assert_almost_equal(loadingList[2].fieldsMapTimes, [0.,1.,2.,3.,4.,5.,6.,7.,8.])
    assert len(loadingList[2].fieldsMapValues) == 9
    assert loadingList[2].fieldsMapValues[0] == 'temperature1.node'
    for i in range(4):
        assert loadingList[2].fieldsMapValues[2*i+1] == 'temperature2.node'
        assert loadingList[2].fieldsMapValues[2*i+2] == 'temperature1.node'
    assert loadingList[2].fieldsMapValues[2] == 'temperature1.node'
    assert loadingList[2].phiAtReducedIntegPoint == None
    assert len(list(loadingList[2].fields.keys())) == 2
    assert 'temperature1.node' in loadingList[2].fields
    assert 'temperature2.node' in loadingList[2].fields
    np.testing.assert_almost_equal(loadingList[2].fields['temperature1.node'],20.+np.zeros(343))
    np.testing.assert_almost_equal(loadingList[2].fields['temperature2.node'],temperatureRef)
    assert loadingList[2].fieldsAtReducedIntegrationPoints == {}


    #Meca Alternate Temp definition
    folder = GetTestDataPath() + "Zset/MecaAlternateTempDefinition/"

    inputFileName = folder + "cube.inp"

    initialCondition = ZIR.ConstructInitialCondition(inputFileName)
    assert initialCondition.dataType == {'U': 'scalar'}
    assert initialCondition.initialSnapshot == {'U': 0.0}
    assert initialCondition.reducedInitialSnapshot == {}

    np.testing.assert_almost_equal(ZIR.ReadInputTimeSequence(inputFileName), timeSequenceRef1)

    loadingList = ZIR.ConstructLoadingsList(inputFileName)
    #loading2
    assert loadingList[2].solutionName == "U"
    assert loadingList[2].set == "ALLNODE"
    assert loadingList[2].type == "temperature"
    np.testing.assert_almost_equal(loadingList[2].fieldsMapTimes, [0.,1.,2.])
    assert len(loadingList[2].fieldsMapValues) == 3
    assert loadingList[2].fieldsMapValues[0] == '0.0'
    assert loadingList[2].fieldsMapValues[1] == '1.0'
    assert loadingList[2].fieldsMapValues[2] == '0.0'
    assert loadingList[2].phiAtReducedIntegPoint == None
    assert len(list(loadingList[2].fields.keys())) == 2
    assert '0.0' in loadingList[2].fields
    assert '1.0' in loadingList[2].fields
    np.testing.assert_almost_equal(loadingList[2].fields['0.0'],20.+np.zeros(343))
    np.testing.assert_almost_equal(loadingList[2].fields['1.0'],temperatureRef)
    assert loadingList[2].fieldsAtReducedIntegrationPoints == {}


    #Thermal
    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    inputFileName = folder + "cube.inp"

    initialCondition = ZIR.ConstructInitialCondition(inputFileName)
    assert initialCondition.dataType == {'T': 'scalar'}
    assert initialCondition.initialSnapshot == {'T': 1000.0}
    assert initialCondition.reducedInitialSnapshot == {}

    np.testing.assert_almost_equal(ZIR.ReadInputTimeSequence(inputFileName), timeSequenceRef3)

    loadingList = ZIR.ConstructLoadingsList(inputFileName)
    #loading0
    assert loadingList[0].solutionName == "T"
    assert loadingList[0].set == "ALLBOUNDARY"
    assert loadingList[0].type == "radiation"
    assert loadingList[0].stefanBoltzmannConstant == 3.9683e-08
    np.testing.assert_almost_equal(loadingList[0].TextTimes, np.array([0.,200.,400.,600.,800.,1000.]))
    np.testing.assert_almost_equal(loadingList[0].TextValues, np.array([1000.,100.,1000.,100.,1000.,100.]))
    assert loadingList[0].reducedPhiT == None

    #loading1
    assert loadingList[1].solutionName == "T"
    assert loadingList[1].set == "ALLBOUNDARY"
    assert loadingList[1].type == "convection_heat_flux"
    np.testing.assert_almost_equal(loadingList[1].hTimes, np.array([0.,1000]))
    np.testing.assert_almost_equal(loadingList[1].hValues, np.array([1000.,1000.]))
    np.testing.assert_almost_equal(loadingList[1].TextTimes, np.array([0.,200.,400.,600.,800.,1000.]))
    np.testing.assert_almost_equal(loadingList[1].TextValues, np.array([1000.,100.,1000.,100.,1000.,100.]))
    assert loadingList[1].reducedPhiT == None
    assert loadingList[1].reducedPhiTPhiT == None

    constitutiveLawsList = ZIR.ConstructConstitutiveLawsList(inputFileName)
    tempTests = [250., 750., 1500.]
    assert constitutiveLawsList[0].set == 'ALLELEMENT'
    assert constitutiveLawsList[0].type == 'thermal'
    np.testing.assert_almost_equal(constitutiveLawsList[0].capacityTemp, np.array([0.,500.,1000.,2000.]))
    assert constitutiveLawsList[0].capacityFunction(tempTests[0]) == 2500000.0
    np.testing.assert_almost_equal(1.e-8*np.array([constitutiveLawsList[0].internalEnergyFunctions[i](tempTests[i]) for i in range(3)]),\
                                   1.e-8*np.array([5.625e+08, 6.875e+08, 1.125e+09]))
    np.testing.assert_almost_equal(constitutiveLawsList[0].internalEnergyConstants, np.array([0.0, 1250000000.0, 2500000000.0]))
    assert constitutiveLawsList[0].conductivityFunction(tempTests[0]) == 9.0
    assert constitutiveLawsList[0].behavior == 'thermal'



    # with string
    #Meca
    folder = GetTestDataPath() + "Zset/MecaSequential/"
    f = open(folder + "cube.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ConstructInitialCondition()
    reader.ReadInputTimeSequence()
    reader.ConstructLoadingsList()
    reader.ConstructConstitutiveLawsList()


    #Meca2
    f = open(folder + "cube2.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ConstructInitialCondition()
    reader.ReadInputTimeSequence()
    reader.ConstructLoadingsList()
    reader.ConstructConstitutiveLawsList()


    #Meca Alternate Temp definition
    folder = GetTestDataPath() + "Zset/MecaAlternateTempDefinition/"

    f = open(folder + "cube.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ConstructInitialCondition()
    reader.ReadInputTimeSequence()
    reader.ConstructLoadingsList()
    reader.ConstructConstitutiveLawsList()


    #Thermal
    folder = GetTestDataPath() + "Zset/ThermalSequential/"

    f = open(folder + "cube.inp", "r")
    string = f.read()
    f.close()

    reader = ZIR.ZsetInputReader(string = string, rootpath = folder)

    reader.ConstructInitialCondition()
    reader.ReadInputTimeSequence()
    reader.ConstructLoadingsList()
    reader.ConstructConstitutiveLawsList()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
