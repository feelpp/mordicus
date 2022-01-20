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
    Class containing an OnlineDataMechanical
    """

    def __init__(self, nReducedIntegrationPoints, numberOfSigmaComponents):
        super(OnlineDataMechanical, self).__init__()

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

        self.reducedIntegrationPoints = None
        self.reducedIntegrationWeights = None
        self.reducedEpsilonAtReducedIntegPoints = None



    def InitializeMaterial(self, tag, var, nstatv, localNbReducedIntegPoints):

        #self.stateVar0[tag]          = np.zeros((localNbReducedIntegPoints,nstatv))
        self.stateVar1[tag]          = np.zeros((localNbReducedIntegPoints,nstatv))

        self.dualVarOutputNames[tag] = var
        self.dualVarOutput[tag]      = {}


    def UpdateInternalStateAtReducedIntegrationPoints(self, time):

        for tag, intPoints in self.indicesOfReducedIntegPointsPerMaterial.items():

            self.stateVar0[tag] = np.copy(self.stateVar1[tag])
            self.dualVarOutput[tag][time] = np.hstack((self.strain1[intPoints],
                                                           self.stress1[intPoints],
                                                           self.stateVar1[tag]))


    def UpdateTemperatureAtReducedIntegrationPoints(self, temperatureAtReducedIntegrationPoints0, temperatureAtReducedIntegrationPoints1):

        assert temperatureAtReducedIntegrationPoints0.shape[0] == self.nReducedIntegrationPoints
        assert temperatureAtReducedIntegrationPoints1.shape[0] == self.nReducedIntegrationPoints

        for tag, intPoints in self.indicesOfReducedIntegPointsPerMaterial.items():

            self.temperature0 = temperatureAtReducedIntegrationPoints0
            self.temperature1 = temperatureAtReducedIntegrationPoints1



    def GetTemperatureAtReducedIntegrationPoints0(self):
        return self.temperature0


    def GetTemperatureAtReducedIntegrationPoints1(self):
        return self.temperature1


    def GetStateVarAtReducedIntegrationPoints0(self, tag):
        assert tag in self.stateVar0, "material with tag "+tag+" not initialized"
        return self.stateVar0[tag]


    def GetStateVarAtReducedIntegrationPoints1(self, tag):
        assert tag in self.stateVar1, "material with tag "+tag+" not initialized"
        return self.stateVar1[tag]


    def SetStateVarAtReducedIntegrationPoints1(self, tag, localStateVar1):
        assert localStateVar1.shape == self.stateVar1[tag].shape
        self.stateVar1[tag] = localStateVar1


    def GetDualVarOutputNames(self, tag):
        assert tag in self.dualVarOutputNames, "material with tag "+tag+" not initialized"
        return self.dualVarOutputNames[tag]


    def GetDualVarOutput(self, tag):
        assert tag in self.dualVarOutput, "material with tag "+tag+" not initialized"
        return self.dualVarOutput[tag]


    def GetStrainAtReducedIntegrationPoints0(self):
        return self.strain0


    def GetStrainAtReducedIntegrationPoints1(self):
        return self.strain1


    def GetStressAtReducedIntegrationPoints1(self):
        return self.stress1


    def SetIndicesOfReducedIntegPointsPerMaterial(self, indicesOfReducedIntegPointsPerMaterial):
        self.indicesOfReducedIntegPointsPerMaterial = indicesOfReducedIntegPointsPerMaterial


    def GetIndicesOfReducedIntegPointsPerMaterial(self):
        return self.indicesOfReducedIntegPointsPerMaterial


    def GetNumberOfSigmaComponents(self):
        return self.numberOfSigmaComponents


    def GetNReducedIntegrationPoints(self):
        return self.nReducedIntegrationPoints


    def GetReducedIntegrationPoints(self):
        return self.reducedIntegrationPoints


    def GetReducedIntegrationWeights(self):
        return self.reducedIntegrationWeights


    def GetReducedEpsilonAtReducedIntegPoints(self):
        return self.reducedEpsilonAtReducedIntegPoints


    def SetStrainAtReducedIntegrationPoints0(self, strain0):
        assert strain0.shape == (self.nReducedIntegrationPoints,self.numberOfSigmaComponents)
        self.strain0 = strain0


    def SetStrainAtReducedIntegrationPoints1(self, strain1):
        assert strain1.shape == (self.nReducedIntegrationPoints,self.numberOfSigmaComponents)
        self.strain1 = strain1


    def SetStressAtReducedIntegrationPoints1(self, stress1):
        assert stress1.shape == (self.nReducedIntegrationPoints,self.numberOfSigmaComponents)
        self.stress1 = stress1


    def SetStrainAtLocalReducedIntegrationPoints1(self, localStrain1, intPoints):
        assert len(intPoints) <= self.nReducedIntegrationPoints
        assert localStrain1.shape[1] == self.numberOfSigmaComponents
        self.strain1[intPoints] = localStrain1


    def SetStressAtLocalReducedIntegrationPoints1(self, localStress1, intPoints):
        assert len(intPoints) <= self.nReducedIntegrationPoints
        assert localStress1.shape[1] == self.numberOfSigmaComponents
        self.stress1[intPoints] = localStress1


    def SetReducedData(self, operatorCompressionData):

        self.reducedIntegrationWeights = operatorCompressionData.GetReducedIntegrationWeights()
        self.reducedIntegrationPoints = operatorCompressionData.GetReducedIntegrationPoints()
        self.reducedEpsilonAtReducedIntegPoints = operatorCompressionData.GetReducedEpsilonAtReducedIntegPoints()


    def __str__(self):
        res = "OnlineDataMechanical"
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


