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


class TestMecaConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a TestMecaConstitutiveLaw ONLY 3D

    Attributes
    ----------
    young : float
        young modulus of the material
    poisson : float
        poisson ratio of the material
    density : float
        density of the material
    constitutiveLawVariables : dict
        dictionary with variable names (str) as keys and variables as type
    """

    def __init__(self, set, young, poisson, density):
        assert isinstance(set, str)

        super(TestMecaConstitutiveLaw, self).__init__(set, "mechanical")

        self.young = young
        self.poisson = poisson
        self.density = density

        lambd = young*poisson/((1+poisson)*(1-2*poisson))
        mu = young/(2*(1+poisson))

        mu2 = 3.5*mu

        self.constitutiveLawVariables = {}
        self.constitutiveLawVariables['nstatv'] = 0
        self.constitutiveLawVariables['ddsdde'] = np.array([[mu2, lambd, lambd, 0., 0., 0.],
                                                            [lambd, mu2, lambd, 0., 0., 0.],
                                                            [lambd, lambd, mu2, 0., 0., 0.],
                                                            [0., 0., 0., mu, 0., 0.],
                                                            [0., 0., 0., 0., mu, 0.],
                                                            [0., 0., 0., 0., 0., mu]])

        self.constitutiveLawVariables['flux'] = ['sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']
        self.constitutiveLawVariables['grad'] = ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31']
        self.constitutiveLawVariables['var_int'] = []
        self.constitutiveLawVariables['var_aux'] = []
        self.constitutiveLawVariables['var_extra'] = []

        self.constitutiveLawVariables['var'] = self.constitutiveLawVariables['grad'] + self.constitutiveLawVariables['flux']



    def GetConstitutiveLawVariables(self):
        """
        Returns
        -------
        dict
            complete dictionary defining the constitutive law variables
        """
        return self.constitutiveLawVariables



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
        np.ndarray
            of size (nbIntPoints, nbeOfDualComponents) stress: stress at the new state
        np.ndarray
            of size (nbIntPoints, nbeOfStateVariables) statev: internal state variables at the new state
        """

        nbIntPoints = stran.shape[0]

        ddsdde = np.tile(self.constitutiveLawVariables['ddsdde'],(nbIntPoints, 1, 1))
        stress = np.einsum('klm,kl->km', ddsdde, stran + dstran, optimize = True)

        return ddsdde, stress, statev


    def UpdateInternalState(self):
        """
        Updates the state of the internal variables
        Not application to the present implementation
        """
        return


    def __str__(self):
        res = "TestMecaConstitutiveLaw on set "+self.set
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)