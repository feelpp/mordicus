# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Helpers import FolderHandler as FH
from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus import GetTestDataPath
import os
import numpy as np


def test():



    folderHandler = FH.FolderHandler(GetTestDataPath()+"Zset"+os.sep+"MecaSequential"+os.sep+"mat")
    folderHandler.SwitchToScriptFolder()

    ZmatLaw = ZIR.ConstructOneMechanicalConstitutiveLaw("./", "mat", "gen_evp", density = 1.e-8, set = "ALLELEMENT")

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

    nstatev = ZmatLaw.GetOneConstitutiveLawVariable("nstatv")
    statev = np.zeros((ngauss,nstatev))

    ddsdde, stress, statev = ZmatLaw.ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)

    np.testing.assert_almost_equal(1.e-5*ddsdde, 1.e-5*np.array( \
    [[[ 1.94601699e+05,  1.52217504e+05,  1.53180797e+05,  1.92658633e+03,  2.40823292e+03 , 2.88987950e+03],
      [ 1.52217504e+05,  1.95564992e+05,  1.52217504e+05, -1.36879431e-10,  -1.68616111e-10, -2.05028129e-10],
      [ 1.53180797e+05,  1.52217504e+05,  1.94601699e+05, -1.92658633e+03,  -2.40823292e+03, -2.88987950e+03],
      [ 1.92658633e+03, -1.66936737e-10, -1.92658633e+03,  1.78205713e+04,  -4.81646583e+03, -5.77975900e+03],
      [ 2.40823292e+03, -2.08300783e-10, -2.40823292e+03, -4.81646583e+03,   1.56531617e+04, -7.22469875e+03],
      [ 2.88987950e+03, -2.49598472e-10, -2.88987950e+03, -5.77975900e+03,  -7.22469875e+03,  1.30041055e+04]]]))

    np.testing.assert_almost_equal(1.e-3*stress, 1.e-3*np.array( \
    [[956.65251203, 1000., 1043.34748797, 86.69497594, 108.36871992, 130.04246391]]))

    np.testing.assert_almost_equal(1.e-2*statev, 1.e-2*np.array( \
    [[ 1.71824133e-03,  2.00000000e-03,  2.28175867e-03,  5.63517344e-04,
       7.04396680e-04,  8.45276015e-04,  3.73209142e-03, -1.51780949e-04,
       1.43589750e-19,  1.51780949e-04,  3.03561899e-04,  3.79452374e-04,
       4.55342848e-04, -7.18241328e-04,  4.91469379e-18,  7.18241328e-04,
       1.43648266e-03,  1.79560332e-03,  2.15472398e-03,  2.93150000e+02]]))


    assert ZmatLaw.GetSet() == 'ALLELEMENT'
    assert ZmatLaw.GetType() == 'mechanical'
    assert ZmatLaw.GetDensity() == 1.e-8
    assert ZmatLaw.GetIdentifier() == ('mechanical', 'ALLELEMENT')


    assert ZmatLaw.GetOneConstitutiveLawVariable("var") ==\
        ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31',\
         'sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31',\
         'eel11', 'eel22', 'eel33', 'eel12', 'eel23', 'eel31', 'evrcum',\
         'al111', 'al122', 'al133', 'al112', 'al123', 'al131',\
         'evri11', 'evri22', 'evri33', 'evri12', 'evri23', 'evri31', 'temp_0']


    assert list(ZmatLaw.GetConstitutiveLawVariables().keys()) ==\
        ['flux', 'grad', 'var_int', 'var_aux', 'var_extra', 'var', 'cmname',\
         'nstatv', 'ndi', 'nshr', 'ntens', 'statev', 'ddsddt', 'drplde',\
         'stress', 'ddsdde', 'sse', 'spd', 'scd', 'rpl', 'drpldt', 'stran',\
         'dstran', 'timesim', 'dtime', 'temperature', 'dtemp', 'predef',\
         'dpred', 'nprops', 'props', 'coords', 'drot', 'pnewdt', 'celent',\
         'dfgrd0', 'dfgrd1', 'noel', 'npt', 'kslay', 'kspt', 'kstep', 'kinc']


    print(ZmatLaw)

    folderHandler.SwitchToExecutionFolder()


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
