# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MfrontConstitutiveLaw as MCL
from Mordicus import GetTestDataPath

import numpy as np


def test():


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


    constitutiveLaw = MCL.MfrontConstitutiveLaw("ALLELEMENT")

    internalVariables = ['eel11', 'eel22', 'eel33', 'eel12', 'eel23', 'eel31', 'epcum']

    constitutiveLaw.SetLawModelling('Tridimensional', 'IsotropicLinearHardeningMises', GetTestDataPath()+'Zset/MecaSequentialSimpleMises/src/libBehaviour.so', internalVariables, ngauss)


    temperature = 293.15 + np.zeros(ngauss)
    dtemp       = np.zeros(ngauss)
    statev = 0.


    ddsdde, stress, statev = constitutiveLaw.ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)

    constitutiveLaw.UpdateInternalState()


    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()
    constitutiveLawVariables = constitutiveLaw.GetConstitutiveLawVariables()
    constitutiveLaw.GetOneConstitutiveLawVariable('var')
    constitutiveLaw.SetConstitutiveLawVariables(constitutiveLawVariables)
    constitutiveLaw.SetOneConstitutiveLawVariable('test', 'test')
    constitutiveLaw.SetDensity(1.)
    constitutiveLaw.GetDensity()


    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
