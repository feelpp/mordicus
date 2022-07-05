# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

from Mordicus.Core.Containers.OnlineData.OnlineDataBase import OnlineDataBase
import numpy as np


class OnlineDataMechanical(OnlineDataBase):
    """
    Class containing an OnlineDataMechanical, used in the online stage
    to store quantities required for the tracking of certain quantites,
    e.g. the internal state variable at the reduced integration points,
    required to compute the constitutive law.

    Attributes
    ----------
    nReducedIntegrationPoints : int
        number of reduced integration points
    numberOfSigmaComponents : int
        number number of second order tensor components
    strain0 : np.ndarray
        of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        strain tensor at reduced integration points, at the beginning of the
        current time step iteration
    strain1 : np.ndarray
        of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        strain tensor at reduced integration points, at the end of the
        current time step iteration
    stress1 : np.ndarray
        of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        stress tensor at reduced integration points, at the end of the
        current time step iteration
    temperature0 : 1D np.ndarray
        of size (nReducedIntegrationPoints,)
        temperature at reduced integration points, at the beginning of the
        current time step iteration
    temperature1 : 1D np.ndarray
        of size (nReducedIntegrationPoints,)
        temperature at reduced integration points, at the end of the
        current time step iteration
    stateVar0 : dict
        with keys the material tags strings, and values np.ndarray of size
        (localNbReducedIntegPoints,nstatv)
        state variable at local reduced integration points (for current material),
        at the beginning of the current time step iteration
    stateVar1 : dict
        with keys the material tags strings, and values np.ndarray of size
        (localNbReducedIntegPoints,nstatv)
        state variable at local reduced integration points (for current material),
        at the end of the current time step iteration
    dualVarOutputNames : dict
        with keys the material tags strings, and values lists of str, containing the
        name of the dual variables chosen for output, and to be reconstructed
    dualVarOutput : dict
        with keys the material tags strings, and values dicts with keys time step,
        and values np.ndarray of size (localNbReducedIntegPoints,
        2*numberOfSigmaComponents+nstatv), containing the values of the
        strain and stress tensors and the state variables for the current material
        and the current time step
    indicesOfReducedIntegPointsPerMaterial : dict
        with keys the material tags strings, and values 1D np.ndarray, the
        ranks of integration points
    """

    def __init__(self, solutionName, nReducedIntegrationPoints, numberOfSigmaComponents):
        super(OnlineDataMechanical, self).__init__(solutionName)

        self.nReducedIntegrationPoints = nReducedIntegrationPoints
        self.numberOfSigmaComponents = numberOfSigmaComponents

        self.strain0 = np.zeros((nReducedIntegrationPoints,numberOfSigmaComponents))
        self.strain1 = np.zeros((nReducedIntegrationPoints,numberOfSigmaComponents))
        self.stress1 = np.zeros((nReducedIntegrationPoints,numberOfSigmaComponents))

        self.temperature0 = np.zeros(nReducedIntegrationPoints)
        self.temperature1 = np.zeros(nReducedIntegrationPoints)

        self.stateVar0 = {}
        self.stateVar1 = {}

        self.dualVarOutputNames = {}
        self.dualVarOutput      = {}

        self.indicesOfReducedIntegPointsPerMaterial = None


    def InitializeMaterial(self, tag, var, nstatv, localNbReducedIntegPoints):
        """
        Initializes stateVar1, dualVarOutputNames and dualVarOutput
        attribute for a material with tag "tag"

        Parameters
        ----------
        tag : str
            tag of the material to be initialized
        var : lists of str
            containing the name of the dual variables chosen for output, and to be reconstructed
        nstatv : int
            number of state variables of the material to be initialized
        localNbReducedIntegPoints : int
            number of reduced integration points that have been selected
            among the integration points in elements from the material to be added
        """
        self.stateVar1[tag]          = np.zeros((localNbReducedIntegPoints,nstatv))
        self.dualVarOutputNames[tag] = var
        self.dualVarOutput[tag]      = {0. : np.zeros((localNbReducedIntegPoints, 2*self.numberOfSigmaComponents+nstatv))}


    def UpdateInternalStateAtReducedIntegrationPoints(self, time):
        """
        Updates the internal state of all the materials at the reduced integration
        points, and at time step value "time"

        Parameters
        ----------
        time : float
            time step value at which the internal state is updated
        """
        for tag, intPoints in self.indicesOfReducedIntegPointsPerMaterial.items():
            self.stateVar0[tag] = np.copy(self.stateVar1[tag])


    def SetDualStateAndVarOutput(self, tag, time, strain, stress, statev):
        """
        Sets stateVar1 and dualVarOutput (at time "time") for material "tag".
        Is called at the end of each Newton iteration. Last value is kept at convergence.

        Parameters
        ----------
        tag : str
            tag of the material whose data is updated
        time : float
            time step when dualVarOutput is set
        strain : np.ndarray
            of size (localNbReducedIntegPoints,numberOfSigmaComponents)
            strain tensor at local reduced integration points of material "tag"
        stress : np.ndarray
            of size (localNbReducedIntegPoints,numberOfSigmaComponents)
            stress tensor at local reduced integration points of material "tag"
        statev : np.ndarray
            of size (localNbReducedIntegPoints,numberOfSigmaComponents)
            state variable at local reduced integration points of material "tag"
        """
        #Voigt convention to invert for output of epsilon
        if self.numberOfSigmaComponents == 6:
            strain[:,3:6] *= 0.5
        elif self.numberOfSigmaComponents == 3: # pragma: no cover
            strain[:,3] *= 0.5

        self.dualVarOutput[tag][time] = np.hstack((strain, stress, statev))
        self.SetStateVarAtReducedIntegrationPoints1(tag, statev)


    def UpdateTemperatureAtReducedIntegrationPoints(self, temperatureAtReducedIntegrationPoints0, temperatureAtReducedIntegrationPoints1):
        """
        Updates the temperature fields at the reduced integration points, at
        the beginning and at the end of the current time step iteration

        Parameters
        ----------
        temperatureAtReducedIntegrationPoints0 : 1D np.ndarray
            of size (nReducedIntegrationPoints,)
            temperature at reduced integration points, at the beginning of the
            current time step iteration
        temperatureAtReducedIntegrationPoints1 : 1D np.ndarray
            of size (nReducedIntegrationPoints,)
            temperature at reduced integration points, at the end of the
            current time step iteration
        """
        self.temperature0 = temperatureAtReducedIntegrationPoints0
        self.temperature1 = temperatureAtReducedIntegrationPoints1


    def GetTemperatureAtReducedIntegrationPoints0(self):
        """
        Get the temperature0 attribute

        Returns
        -------
        1D np.ndarray
            of size (nReducedIntegrationPoints,)
        """
        return self.temperature0


    def GetTemperatureAtReducedIntegrationPoints1(self):
        """
        Get the temperature1 attribute

        Returns
        -------
        1D np.ndarray
            of size (nReducedIntegrationPoints,)
        """
        return self.temperature1


    def GetStateVarAtReducedIntegrationPoints0(self, tag):
        """
        Get the stateVar0 attribute

        Returns
        -------
        dict
            with keys the material tags strings, and values np.ndarray of size
            (localNbReducedIntegPoints,nstatv)
        """
        return self.stateVar0[tag]


    def GetStateVarAtReducedIntegrationPoints1(self, tag):
        """
        Get the stateVar1 attribute

        Returns
        -------
        dict
            with keys the material tags strings, and values np.ndarray of size
            (localNbReducedIntegPoints,nstatv)
        """
        return self.stateVar1[tag]


    def GetDualVarOutputNames(self, tag):
        """
        Get the dualVarOutputNames attribute associated to the material with tag "tag"

        Returns
        -------
        list
            dualVarOutputNames[tag], list of str
        """
        return self.dualVarOutputNames[tag]


    def GetDualVarOutput(self, tag):
        """
        Get the GetDualVarOutput attribute associated to the material with tag "tag"

        Returns
        -------
        dict
            dualVarOutput[tag], with keys time step, and values np.ndarray of size
            (localNbReducedIntegPoints,2*numberOfSigmaComponents+nstatv)
        """
        return self.dualVarOutput[tag]


    def GetStrainAtReducedIntegrationPoints0(self):
        """
        Get the strain0 attribute

        Returns
        -------
        np.ndarray
            strain0, of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        """
        return self.strain0


    def GetStrainAtReducedIntegrationPoints1(self):
        """
        Get the strain1 attribute

        Returns
        -------
        np.ndarray
            strain1, of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        """
        return self.strain1


    def GetStressAtReducedIntegrationPoints1(self):
        """
        Get the stress1 attribute

        Returns
        -------
        np.ndarray
            stress1, of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        """
        return self.stress1


    def GetIndicesOfReducedIntegPointsPerMaterial(self):
        """
        Get the indicesOfReducedIntegPointsPerMaterial attribute

        Returns
        -------
        dict
            indicesOfReducedIntegPointsPerMaterial, with keys the material tags strings, and values 1D np.ndarray, the
            ranks of integration points
        """
        return self.indicesOfReducedIntegPointsPerMaterial


    def GetNumberOfSigmaComponents(self):
        """
        Get the numberOfSigmaComponents attribute

        Returns
        -------
        int
            numberOfSigmaComponents
        """
        return self.numberOfSigmaComponents


    def GetNReducedIntegrationPoints(self):
        """
        Get the nReducedIntegrationPoints attribute

        Returns
        -------
        int
            nReducedIntegrationPoints
        """
        return self.nReducedIntegrationPoints


    def SetIndicesOfReducedIntegPointsPerMaterial(self, indicesOfReducedIntegPointsPerMaterial):
        """
        Sets the indicesOfReducedIntegPointsPerMaterial attribute

        Parameters
        ----------
        indicesOfReducedIntegPointsPerMaterial : dict
            with keys the material tags strings, and values 1D np.ndarray, the
            ranks of integration points
        """
        self.indicesOfReducedIntegPointsPerMaterial = indicesOfReducedIntegPointsPerMaterial


    def SetStateVarAtReducedIntegrationPoints1(self, tag, localStateVar1):
        """
        Sets the stateVar1 attribute associated to the material with tag "tag"

        Parameters
        ----------
        tag : int
            tag of the material
        localStateVar1 : np.ndarray
            of size (localNbReducedIntegPoints,nstatv)
        """
        self.stateVar1[tag] = localStateVar1


    def SetStrainAtReducedIntegrationPoints0(self, strain0):
        """
        Sets the strain0 attribute

        Parameters
        ----------
        strain0 : np.ndarray
            of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        """
        self.strain0 = strain0


    def SetStrainAtReducedIntegrationPoints1(self, strain1):
        """
        Sets the strain1 attribute

        Parameters
        ----------
        strain1 : np.ndarray
            of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        """
        self.strain1 = strain1


    def SetStressAtReducedIntegrationPoints1(self, stress1):
        """
        Sets the stress1 attribute

        Parameters
        ----------
        stress1 : np.ndarray
            of size (nReducedIntegrationPoints,numberOfSigmaComponents)
        """
        self.stress1 = stress1


    def SetStrainAtLocalReducedIntegrationPoints1(self, localStrain1, intPoints):
        """
        Sets the strain1 attribute at certain reduced integration points

        Parameters
        ----------
        localStrain1 : np.ndarray
            of size (localNbReducedIntegPoints,numberOfSigmaComponents)
        intPoints : 1D np.ndarray
            of size (localNbReducedIntegPoints,)
        """
        self.strain1[intPoints] = localStrain1


    def SetStressAtLocalReducedIntegrationPoints1(self, localStress1, intPoints):
        """
        Sets the stress1 attribute at certain reduced integration points

        Parameters
        ----------
        localStress1 : np.ndarray
            of size (localNbReducedIntegPoints,numberOfSigmaComponents)
        intPoints : 1D np.ndarray
            of size (localNbReducedIntegPoints,)
        """
        self.stress1[intPoints] = localStress1


    def __str__(self):
        res = "OnlineDataMechanical, associated to solution "+self.solutionName
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


