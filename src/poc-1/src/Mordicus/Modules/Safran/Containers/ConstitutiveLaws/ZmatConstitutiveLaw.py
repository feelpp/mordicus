# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase
import numpy as np


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

        self.constitutiveLawVariables = constitutiveLawVariables


    def SetOneConstitutiveLawVariable(self, var, value):

        self.constitutiveLawVariables[var] = value


    def SetDensity(self, density):
        self.density = density


    def SetBehavior(self, behavior):
        self.behavior = behavior


    def GetConstitutiveLawVariables(self):

        return self.constitutiveLawVariables


    def GetOneConstitutiveLawVariable(self, var):

        return self.constitutiveLawVariables[var]


    def GetDensity(self):

        return self.density


    def ComputeConstitutiveLaw(self, temperature, dtemp, stran, dstran, statev):

        from Mordicus.Modules.Safran.External.pyumat import py3umat as pyumat

        nbIntPoints = stran.shape[0]

        stress = np.empty(stran.shape)
        ddsdde = np.empty((nbIntPoints , stran.shape[1], stran.shape[1]))

        for k in range(nbIntPoints):

            ddsdde[k,:,:] = pyumat.umat(stress=self.constitutiveLawVariables['stress'], statev=statev[k,:], ddsdde=self.constitutiveLawVariables['ddsdde'], sse=self.constitutiveLawVariables['sse'], spd=self.constitutiveLawVariables['spd'], scd=self.constitutiveLawVariables['scd'], rpl=self.constitutiveLawVariables['rpl'], ddsddt=self.constitutiveLawVariables['ddsddt'], drplde=self.constitutiveLawVariables['drplde'], drpldt=self.constitutiveLawVariables['drpldt'], stran=stran[k,:],  dstran=dstran[k,:], time=self.constitutiveLawVariables['timesim'], dtime=self.constitutiveLawVariables['dtime'], temp=temperature[k], dtemp=dtemp[k], predef=self.constitutiveLawVariables['predef'], dpred=self.constitutiveLawVariables['dpred'], cmname=self.constitutiveLawVariables['cmname'], ndi=self.constitutiveLawVariables['ndi'], nshr=self.constitutiveLawVariables['nshr'], ntens=self.constitutiveLawVariables['ntens'], nstatv=self.constitutiveLawVariables['nstatv'], props=self.constitutiveLawVariables['props'], nprops=self.constitutiveLawVariables['nprops'], coords=self.constitutiveLawVariables['coords'], drot=self.constitutiveLawVariables['drot'], pnewdt=self.constitutiveLawVariables['pnewdt'], celent=self.constitutiveLawVariables['celent'], dfgrd0=self.constitutiveLawVariables['dfgrd0'], dfgrd1=self.constitutiveLawVariables['dfgrd1'], noel=self.constitutiveLawVariables['noel'], npt=self.constitutiveLawVariables['npt'], kslay=self.constitutiveLawVariables['kslay'], kspt=self.constitutiveLawVariables['kspt'], kstep=self.constitutiveLawVariables['kstep'], kinc=self.constitutiveLawVariables['kinc'])

            stress[k,:] = self.constitutiveLawVariables['stress']

        #stran[:,3:6] /= 2.
        #stran[:,4:6] = stran[:,[5,4]]

        return ddsdde, stress



    def __str__(self):
        res = "Mechanical ZmatConstitutiveLaw on set "+self.set
        return res
