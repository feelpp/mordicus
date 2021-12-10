# -*- coding: utf-8 -*-
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
        self.constitutiveLawVariables['ddsdde'] = np.array([[mu2, lambd, lambd,      0.,       0.,         0.], [lambd, mu2, lambd,      0.,       0.,         0.], [lambd, lambd, mu2,      0.,       0.,         0.], [0.,              0.,              0.,         mu,      0.,       0.], [0.,              0.,              0.,              0.,  mu,      0.], [0.,              0.,              0.,              0.,       0.,         mu]])

        self.constitutiveLawVariables['flux'] = ['sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']
        self.constitutiveLawVariables['grad'] = ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31']
        self.constitutiveLawVariables['var_int'] = []
        self.constitutiveLawVariables['var_aux'] = []
        self.constitutiveLawVariables['var_extra'] = []

        self.constitutiveLawVariables['var'] = self.constitutiveLawVariables['grad'] + self.constitutiveLawVariables['flux']



    def GetConstitutiveLawVariables(self):

        return self.constitutiveLawVariables



    def SetOneConstitutiveLawVariable(self, var, value):

        self.constitutiveLawVariables[var] = value



    def GetOneConstitutiveLawVariable(self, var):

        return self.constitutiveLawVariables[var]



    def GetDensity(self):

        return self.density


    def ComputeConstitutiveLaw(self, temperature, dtemp, stran, dstran, statev):

        nbIntPoints = stran.shape[0]

        ddsdde = np.tile(self.constitutiveLawVariables['ddsdde'],(nbIntPoints, 1, 1))
        stress = np.einsum('klm,kl->km', ddsdde, stran, optimize = True)

        return ddsdde, stress, statev


    def UpdateInternalState(self):
        return


    def __str__(self):
        res = "TestMecaConstitutiveLaw on set "+self.set
        return res
