# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase
import numpy as np
from BasicTools.Containers import SymExpr as SE
from scipy.interpolate import interp1d

class ThermalConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a ThermalConstitutiveLaw

    Attributes
    ----------
    thermalCapacity : scipy.interpolate.interp1d instance
        thermalCapacity function
    thermalConductivity : scipy.interpolate.interp1d instance
        thermalConductivity function
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(ThermalConstitutiveLaw, self).__init__(set, "thermal")
        self.thermalCapacity = None
        self.thermalConductivity = None
        self.behavior = None


    def SetBehavior(self, behavior):
        self.behavior = behavior


    def SetThermalCapacity(self, capacityTemp, capacityVal):

        self.thermalCapacity = interp1d(capacityTemp, capacityVal)


    def SetThermalConductivity(self, conductivityTemp, conductivityVal):

        self.thermalConductivity = interp1d(conductivityTemp, conductivityVal)


    def ComputeConstitutiveLaw(self, temperature):

        return float(self.thermalCapacity(temperature)), float(self.thermalConductivity(temperature))


    def GetIdentifier(self):
        """
        Returns
        -------
        couple of strings (set, type)
            the identifier of constitutive law
        """
        return self.set


    def __str__(self):
        res = "ThermalConstitutiveLaw on set "+self.set
        return res
