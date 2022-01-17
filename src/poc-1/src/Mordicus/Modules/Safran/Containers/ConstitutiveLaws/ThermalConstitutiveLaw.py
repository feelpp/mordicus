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
from Mordicus.Core.BasicAlgorithms import Interpolation as TI
from scipy import integrate, interpolate



class ThermalConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a ThermalConstitutiveLaw
    thermal capacity (in J.K-1.kg-1) and thermal conductivity (in W.K-1.m-1)
    are modeled as piecewise linear functions of the temperature

    Attributes
    ----------
    capacityTemp : np.ndarray or list of floats
        temperature values on which thermal capacities are provided
    capacityFunction : scipy.interpolate.interp1d
        thermal capacity as a piecewise linear functions of the temperature
    internalEnergyFunctions : list of scipy.interpolate.interp1d
        internal energy modeled as a set of piecewise linear functions of the
        temperature up to a constant
    internalEnergyConstants : np.ndarray or list of floats
        additive constants associated to internalEnergyFunctions
    conductivityFunction : scipy.interpolate.interp1d
        thermal conductivity as a piecewise linear functions of the temperature
    behavior : str
        name of the model behavior
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
        """
        Sets the name of the model behavior

        Parameters
        ----------
        behavior : str
            name of the model behavior
        """
        self.behavior = behavior


    def SetThermalCapacity(self, capacityTemp, capacityVal):
        """
        Sets the model of thermal capacity

        Parameters
        ----------
        capacityTemp : np.ndarray or list of floats
            temperature values on which thermal capacity are provided
        capacityVal : np.ndarray or list of floats
            thermal capacity values on corresponding temperature values
        """

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
        """
        Sets the model of thermal conductivity

        Parameters
        ----------
        conductivityTemp : np.ndarray or list of floats
            temperature values on which thermal conductivity values are provided
        conductivityVal : np.ndarray or list of floats
            thermal conductivity values on corresponding temperature values
        """

        self.conductivityFunction = interpolate.interp1d(conductivityTemp, conductivityVal, kind='linear',  copy=True, bounds_error=False, assume_sorted=True)


    def ComputeCapacity(self, temperature):
        """
        Computes the thermal capacity for a given temperature value

        Parameters
        ----------
        temperature : float
            temperature at which the capacity is computed

        Returns
        -------
        float
            thermal capacity
        """

        return self.capacityFunction(temperature)


    def ComputeConductivity(self, temperature):
        """
        Computes the thermal conductivity for a given temperature value

        Parameters
        ----------
        temperature : float
            temperature at which the conductivity is computed

        Returns
        -------
        float
            thermal conductivity
        """

        return self.conductivityFunction(temperature)


    def ComputeInternalEnergy(self, temperature):
        """
        Computes the internal energy for a given temperature value

        Parameters
        ----------
        temperature : float
            temperature at which the conductivity is computed

        Returns
        -------
        float
            internal energy
        """

        previousTempStep = TI.BinarySearch(self.capacityTemp, temperature)

        return self.internalEnergyConstants[previousTempStep] + self.internalEnergyFunctions[previousTempStep](temperature)


    def ComputeInternalEnergyVectorized(self, temperature):
        """
        Computes the internal energy for a set of given temperature values

        Notes
        -----
        Out of bounds: we take for internal energy the constant value of the
        bound, not extrapolate the primitive

        Parameters
        ----------
        temperature : np.ndarray or list of floats
            temperature values at which the internal energy is computed

        Returns
        -------
        np.ndarray of floats
            set of internal energy values
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


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)