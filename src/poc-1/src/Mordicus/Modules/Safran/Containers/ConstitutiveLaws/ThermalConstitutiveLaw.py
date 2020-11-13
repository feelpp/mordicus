# -*- coding: utf-8 -*-
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase
from Mordicus.Core.BasicAlgorithms import Interpolation as TI
from scipy import integrate, interpolate



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
        self.capacityFunction = None
        self.internalEnergyFunctions = None
        self.internalEnergyConstants = None
        self.conductivityFunction = None
        self.behavior = None


    def SetBehavior(self, behavior):
        self.behavior = behavior


    def SetThermalCapacity(self, capacityTemp, capacityVal):

        self.capacityTemp = capacityTemp

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


        self.capacityFunction = interpolate.interp1d(capacityTemp, capacityVal, kind='linear',  copy=True, bounds_error=False, assume_sorted=True)



    def SetThermalConductivity(self, conductivityTemp, conductivityVal):

        self.conductivityFunction = interpolate.interp1d(conductivityTemp, conductivityVal, kind='linear',  copy=True, bounds_error=False, assume_sorted=True)



    def ComputeCapacity(self, temperature):

        return self.capacityFunction(temperature)


    def ComputeConductivity(self, temperature):

        return self.conductivityFunction(temperature)


    def ComputeInternalEnergy(self, temperature):

        previousTempStep = TI.BinarySearch(self.capacityTemp, temperature)

        return self.internalEnergyConstants[previousTempStep] + self.internalEnergyFunctions[previousTempStep](temperature)


    def ComputeInternalEnergyVectorized(self, temperature):

        """
        Out of bounds: we take for internal energy the constant value of the bound, not extrapolate the primitive
        """

        temperature = np.array(temperature)

        previousTempStep = TI.BinarySearchVectorized(self.capacityTemp, temperature)

        underOutOfBoundsInidices = temperature <= self.capacityTemp[0]
        overOutOfBoundsInidices = temperature >= self.capacityTemp[-1]

        previousTempStep[underOutOfBoundsInidices]  = -1
        previousTempStep[overOutOfBoundsInidices] = -1

        res = np.empty(temperature.size)

        res[underOutOfBoundsInidices]  = self.internalEnergyConstants[0]
        res[overOutOfBoundsInidices] = self.internalEnergyConstants[-1] + self.internalEnergyFunctions[-1](self.capacityTemp[-1])

        for i in range(len(self.capacityTemp)):
            indices = previousTempStep == i
            localTemperature = temperature[indices]
            if localTemperature.size > 0:
                res[indices] = self.internalEnergyConstants[i] + self.internalEnergyFunctions[i](localTemperature)

        return res



    def __str__(self):
        res = "ThermalConstitutiveLaw on set "+self.set
        return res
