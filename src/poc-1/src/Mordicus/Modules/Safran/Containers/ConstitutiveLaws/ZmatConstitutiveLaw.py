# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase


import sys
if "vtkpython" in sys.executable:# pragma: no cover
    from Mordicus.Modules.Safran.External.pvpyumat import py3umat as pyumat
else:
    from Mordicus.Modules.Safran.External.pyumat import py3umat as pyumat

indices = [0,1,2,3,5,4]
#indices = [0,1,2,3,4,5]

class ZmatConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a ZmatConstitutiveLaw

    Attributes
    ----------
    constitutiveLawVariables : dict
        dictionary with variable names (str) as keys and variables as type
    density : float
        density of the material
    behavior : str
        Z-mat behavior keyword
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(ZmatConstitutiveLaw, self).__init__(set, "mechanical")

        self.constitutiveLawVariables = {}
        self.density = None
        self.behavior = None


    def SetConstitutiveLawVariables(self, constitutiveLawVariables):
        """
        Sets the constitutiveLawVariables dictionary

        Parameters
        ----------
        constitutiveLawVariables : dict
            dictionary with variable names (str) as keys and variables as type
        """
        self.constitutiveLawVariables = constitutiveLawVariables


    def SetOneConstitutiveLawVariable(self, var, value):
        """
        Sets one variable of the constitutive law

        Parameters
        ----------
        var : str
            name of the variable
        value : custom_data_structure
            variable of the constitutive law
        """
        self.constitutiveLawVariables[var] = value


    def SetDensity(self, density):
        """
        Sets the density of the constitutive law

        Parameters
        ----------
        density : float
            density of the material
        """
        self.density = density


    def SetBehavior(self, behavior):
        """
        Sets the name of the model behavior

        Parameters
        ----------
        behavior : str
            name of the model behavior
        """
        self.behavior = behavior


    def GetConstitutiveLawVariables(self):
        """
        Returns
        -------
        dict
            complete dictionary defining the constitutive law variables
        """
        return self.constitutiveLawVariables


    def GetOneConstitutiveLawVariable(self, var):
        """
        Returns one variable of the constitutive law

        Parameters
        ----------
        var : str
            key of the dictionnary for storing the variable (e.g. name of the variable)

        Returns
        -------
        custom_data_structure
            variable of the constitutive law
        """
        return self.constitutiveLawVariables[var]


    def GetDensity(self):
        """
        Returns the density of the material

        Returns
        -------
        float
            density
        """
        return self.density


    def ComputeConstitutiveLaw(self, temperature, dtemp, stran, dstran, statev):
        """
        Main function of the class: computes a new material state using a constitutive law
        solver from a previous material state and variations of temperature and strain

        Parameters
        ----------
        temperature : 1D np.ndarray or list
            temperature at the previous state, at integration points (np.ndarray of size (nbIntPoints) or list of length nbIntPoints)
        dtemp : 1D np.ndarray or list
            variations of temperature between the previous state and the new state to compute,
            at integration points (np.ndarray of size (nbIntPoints) or list of length nbIntPoints)
        stran : np.ndarray
            strain at the previous state, at integration points (np.ndarray of size (nbIntPoints,nbeOfDualComponents))
        dstran : np.ndarray
            variations of strain between the previous state and the new state to compute,
            at integration points (np.ndarray of size (nbIntPoints,nbeOfDualComponents))
        statev : np.ndarray
            internal state variables at the previous state, at integration points (np.ndarray of size (nbIntPoints,nbeOfStateVariables))

        Returns
        -------
        np.ndarray
            of size (nbIntPoints, nbeOfDualComponents, nbeOfDualComponents) ddsdde: local tangent matrix at the new state
        np.ndarray
            of size (nbIntPoints, nbeOfDualComponents) stress: stress at the new state
        np.ndarray
            of size (nbIntPoints, nbeOfStateVariables) statev: internal state variables at the new state
        """

        nbIntPoints = stran.shape[0]

        stress = np.empty(stran.shape)
        ddsdde = np.empty((nbIntPoints , stran.shape[1], stran.shape[1]))

        stran = stran[:,indices]
        dstran = dstran[:,indices]

        for k in range(nbIntPoints):

            ddsdde[k,:,:] = self.PyumatCall(k, temperature, dtemp, stran, dstran, statev)

            stress[k,:] = self.constitutiveLawVariables['stress']

        ddsdde = ddsdde[:,:,indices]
        ddsdde = ddsdde[:,indices,:]

        stress = stress[:,indices]

        return ddsdde, stress, statev


    def PyumatCall(self, k, temperature, dtemp, stran, dstran, statev):
        """
        Computes a new material state using a constitutive law solver from a
        previous material state and variations of temperature and strain at
        the integration point ranked k

        Parameters
        ----------
        temperature : np.ndarray or list
            temperature at the previous state, at integration points (np.ndarray of size (nbIntPoints) or list of length nbIntPoints)
        dtemp : np.ndarray or list
            variations of temperature between the previous state and the new state to compute,
            at integration points (np.ndarray of size (nbIntPoints) or list of length nbIntPoints)
        stran : np.ndarray
            strain at the previous state, at integration points (np.ndarray of size (nbIntPoints,nbeOfDualComponents))
        dstran : np.ndarray
            variations of strain between the previous state and the new state to compute,
            at integration points (np.ndarray of size (nbIntPoints,nbeOfDualComponents))
        statev : np.ndarray
            internal state variables at the previous state, at integration points (np.ndarray of size (nbIntPoints,nbeOfStateVariables))

        Returns
        -------
        np.ndarray
            of size (nbIntPoints, nbeOfDualComponents, nbeOfDualComponents) ddsdde: local tangent matrix at the new state
        """

        return pyumat.umat(stress=self.constitutiveLawVariables['stress'],
                           statev=statev[k,:],
                           ddsdde=self.constitutiveLawVariables['ddsdde'],
                           sse=self.constitutiveLawVariables['sse'],
                           spd=self.constitutiveLawVariables['spd'],
                           scd=self.constitutiveLawVariables['scd'],
                           rpl=self.constitutiveLawVariables['rpl'],
                           ddsddt=self.constitutiveLawVariables['ddsddt'],
                           drplde=self.constitutiveLawVariables['drplde'],
                           drpldt=self.constitutiveLawVariables['drpldt'],
                           stran=stran[k,:],
                           dstran=dstran[k,:],
                           time=self.constitutiveLawVariables['timesim'],
                           dtime=self.constitutiveLawVariables['dtime'],
                           temp=temperature[k],
                           dtemp=dtemp[k],
                           predef=self.constitutiveLawVariables['predef'],
                           dpred=self.constitutiveLawVariables['dpred'],
                           cmname=self.constitutiveLawVariables['cmname'],
                           ndi=self.constitutiveLawVariables['ndi'],
                           nshr=self.constitutiveLawVariables['nshr'],
                           ntens=self.constitutiveLawVariables['ntens'],
                           nstatv=self.constitutiveLawVariables['nstatv'],
                           props=self.constitutiveLawVariables['props'],
                           nprops=self.constitutiveLawVariables['nprops'],
                           coords=self.constitutiveLawVariables['coords'],
                           drot=self.constitutiveLawVariables['drot'],
                           pnewdt=self.constitutiveLawVariables['pnewdt'],
                           celent=self.constitutiveLawVariables['celent'],
                           dfgrd0=self.constitutiveLawVariables['dfgrd0'],
                           dfgrd1=self.constitutiveLawVariables['dfgrd1'],
                           noel=self.constitutiveLawVariables['noel'],
                           npt=self.constitutiveLawVariables['npt'],
                           kslay=self.constitutiveLawVariables['kslay'],
                           kspt=self.constitutiveLawVariables['kspt'],
                           kstep=self.constitutiveLawVariables['kstep'],
                           kinc=self.constitutiveLawVariables['kinc'])


    def UpdateInternalState(self):
        """
        Updates the state of the internal variables
        Not application to the present implementation
        """
        return


    def __str__(self):
        res = "Mechanical ZmatConstitutiveLaw on set "+self.set
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)