# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MfrontConstitutiveLaw as MCL
from Mordicus import GetTestDataPath
from Mordicus.Core.Helpers import FolderHandler as FH


import numpy as np
import os

def test():

    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()

    constitutiveLaw = MCL.MfrontConstitutiveLaw("ALLELEMENT")


    assert constitutiveLaw.GetSet() == 'ALLELEMENT'
    assert constitutiveLaw.GetType() == 'mechanical'
    assert constitutiveLaw.GetIdentifier() == ('mechanical', 'ALLELEMENT')
    constitutiveLaw.SetOneConstitutiveLawVariable('test', 'test')
    assert constitutiveLaw.GetOneConstitutiveLawVariable('test') == 'test'
    constitutiveLaw.SetDensity(1.)
    assert constitutiveLaw.GetDensity() == 1.


    ngauss = 1

    temperature = 293.15 + np.zeros(ngauss)
    dtemp       = np.zeros(ngauss)
    stran = np.zeros((ngauss,6))
    dstran = np.zeros((ngauss,6))
    dstran[:,0] = 1.
    dstran[:,1] = 2.
    dstran[:,2] = 3.
    dstran[:,3] = 4.
    dstran[:,4] = 5.
    dstran[:,5] = 6.

    dstran[:,:] *= 0.001

    folder = GetTestDataPath()+'Zset'+os.sep+'MecaSequentialSimpleMises'+os.sep


    #uncomment for testing (mfront must be compiled on corresponding architecture)
    """if os.path.isfile(folder+'src/libBehaviour.so') == False:
        import subprocess
        os.chdir(folder)
        subprocess.call("./compileMfrontLaw.sh")

    internalVariables = ['eel11', 'eel22', 'eel33', 'eel12', 'eel23', 'eel31', 'epcum']
    constitutiveLaw.SetLawModelling('Tridimensional', 'IsotropicLinearHardeningMises', folder+'src'+os.sep+'libBehaviour.so', internalVariables, ngauss)

    temperature = 293.15 + np.zeros(ngauss)
    dtemp       = np.zeros(ngauss)
    statev = 0.

    ddsdde, stress, statev = constitutiveLaw.ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)

    constitutiveLaw.UpdateInternalState()

    constitutiveLawVariables = constitutiveLaw.GetConstitutiveLawVariables()
    assert constitutiveLawVariables['var'] == ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31',\
            'sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31', 'eel11', 'eel22', 'eel33', 'eel12', 'eel23', 'eel31', 'epcum']
    constitutiveLaw.SetConstitutiveLawVariables(constitutiveLawVariables)"""

    print(constitutiveLaw)

    folderHandler.SwitchToExecutionFolder()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
