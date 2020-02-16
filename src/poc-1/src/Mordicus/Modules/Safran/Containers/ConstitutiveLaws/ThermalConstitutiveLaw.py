# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase
import numpy as np
from Mordicus.Core.BasicAlgorithms import Interpolation as TI
from scipy import integrate,interpolate

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
        self.capacityTemp = None
        self.capacityVal = None
        self.internalEnergyFunctions = None
        self.internalEnergyConstants = None
        self.conductivityTemp = None
        self.conductivityVal = None
        self.behavior = None


    def SetBehavior(self, behavior):
        self.behavior = behavior


    def SetThermalCapacity(self, capacityTemp, capacityVal):

        self.capacityTemp = capacityTemp
        self.capacityVal = capacityVal

        self.internalEnergyFunctions = []
        self.internalEnergyConstants = []

        constant = 0.
        for i in range(len(capacityTemp)-1):
            xx = np.array([capacityTemp[i], 0.5*(capacityTemp[i]+capacityTemp[i+1]), capacityTemp[i+1]])
            yy = np.array([capacityVal[i], 0.5*(capacityVal[i]+capacityVal[i+1]), capacityVal[i+1]])
            y_int = integrate.cumtrapz(y = yy , x = xx, initial = 0.)

            self.internalEnergyFunctions.append(interpolate.interp1d(xx, y_int, kind='quadratic',  copy=True, bounds_error=False, assume_sorted=True))
            self.internalEnergyConstants.append(constant)

            constant += y_int[-1]

    def SetThermalConductivity(self, conductivityTemp, conductivityVal):

        self.conductivityTemp = conductivityTemp
        self.conductivityVal = conductivityVal


    def ComputeCapacity(self, temperature):

        return TI.PieceWiseLinearInterpolation(temperature, self.capacityTemp, self.capacityVal)



    def ComputeCapacityVectorized(self, temperature):

        return TI.PieceWiseLinearInterpolationVectorized(temperature, self.capacityTemp, self.capacityVal)


    def ComputeConductivity(self, temperature):

        return TI.PieceWiseLinearInterpolation(temperature, self.conductivityTemp, self.conductivityVal)


    def ComputeConductivityVectorized(self, temperature):

        return TI.PieceWiseLinearInterpolationVectorized(temperature, self.conductivityTemp, self.conductivityVal)


    def ComputeInternalEnergy(self, temperature):

        previousTempStep = TI.BinarySearch(self.capacityTemp, temperature)

        return self.internalEnergyConstants[previousTempStep] + self.internalEnergyFunctions[previousTempStep](temperature)


    def ComputeInternalEnergyVectorized(self, temperature):

        temperature = np.array(temperature)

        previousTempStep = TI.BinarySearchVectorized(self.capacityTemp, temperature)

        res = np.empty(temperature.size)
        for i in range(len(self.capacityTemp)):
            indices = previousTempStep == i
            localTemperature = temperature[indices]
            if localTemperature.size > 0:
                res[indices] = self.internalEnergyConstants[i] + self.internalEnergyFunctions[i](localTemperature)

        return res



    def __str__(self):
        res = "ThermalConstitutiveLaw on set "+self.set
        return res
