# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.OnlineData import OnlineDataMechanical as ODM
import numpy as np

def test():

    onlineDataMechanical = ODM.OnlineDataMechanical("U", 4, 2)

    onlineDataMechanical.InitializeMaterial("ALLELEMENT", ['eto11', 'eto22', 'evrcum'], 3, 4)

    indicesOfReducedIntegPointsPerMaterial = {'ALLELEMENT': np.arange(4)}
    onlineDataMechanical.SetIndicesOfReducedIntegPointsPerMaterial(indicesOfReducedIntegPointsPerMaterial)
    onlineDataMechanical.UpdateInternalStateAtReducedIntegrationPoints(0.)

    onlineDataMechanical.UpdateTemperatureAtReducedIntegrationPoints(np.array([20., 20., 20., 20.]), np.array([21., 22., 21., 23.]))

    test = np.ones(4)
    onlineDataMechanical.SetStrainAtReducedIntegrationPoints0(test)
    assert id(onlineDataMechanical.GetStrainAtReducedIntegrationPoints0()) == id(test)

    test = np.ones(4)
    onlineDataMechanical.SetStrainAtReducedIntegrationPoints1(test)
    assert id(onlineDataMechanical.GetStrainAtReducedIntegrationPoints1()) == id(test)

    test = np.ones(4)
    onlineDataMechanical.SetStressAtReducedIntegrationPoints1(test)
    assert id(onlineDataMechanical.GetStressAtReducedIntegrationPoints1()) == id(test)


    onlineDataMechanical.SetStrainAtLocalReducedIntegrationPoints1(np.ones(4), np.arange(4))
    np.testing.assert_almost_equal(onlineDataMechanical.GetStrainAtReducedIntegrationPoints1()[np.arange(4)], np.ones(4))

    onlineDataMechanical.SetStressAtLocalReducedIntegrationPoints1(np.ones(4), np.arange(4))
    np.testing.assert_almost_equal(onlineDataMechanical.GetStressAtReducedIntegrationPoints1()[np.arange(4)], np.ones(4))


    onlineDataMechanical.SetStateVarAtReducedIntegrationPoints1('ALLELEMENT', np.ones(4))
    np.testing.assert_almost_equal(onlineDataMechanical.GetStateVarAtReducedIntegrationPoints1('ALLELEMENT'), np.ones(4))

    np.testing.assert_almost_equal(onlineDataMechanical.GetStateVarAtReducedIntegrationPoints0('ALLELEMENT'), np.zeros((4,3)))


    np.testing.assert_almost_equal(onlineDataMechanical.GetTemperatureAtReducedIntegrationPoints0(), np.array([20., 20., 20., 20.]))
    np.testing.assert_almost_equal(onlineDataMechanical.GetTemperatureAtReducedIntegrationPoints1(), np.array([21., 22., 21., 23.]))

    test = onlineDataMechanical.GetIndicesOfReducedIntegPointsPerMaterial()
    assert list(test.keys()) == ['ALLELEMENT']
    np.testing.assert_almost_equal(test['ALLELEMENT'], np.arange(4))

    assert onlineDataMechanical.GetNumberOfSigmaComponents() == 2
    assert onlineDataMechanical.GetNReducedIntegrationPoints() == 4

    assert onlineDataMechanical.GetDualVarOutputNames('ALLELEMENT') == ['eto11', 'eto22', 'evrcum']
    test = onlineDataMechanical.GetDualVarOutput('ALLELEMENT')
    assert list(test.keys()) == [0.]
    assert onlineDataMechanical.GetDualVarOutput('ALLELEMENT')[0.].shape == (4,7)


    print(onlineDataMechanical)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
