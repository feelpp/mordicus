# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OperatorCompressionData.OperatorCompressionDataBase import OperatorCompressionDataBase



class OperatorCompressionDataMechanical(OperatorCompressionDataBase):
    """
    Class containing an OperatorCompressionDataMechanical
    """

    def __init__(self, gradPhiAtIntegPoint, integrationWeights, listOfTags):
        super(OperatorCompressionDataMechanical, self).__init__()

        self.gradPhiAtIntegPoint = gradPhiAtIntegPoint
        self.integrationWeights = integrationWeights
        self.listOfTags = listOfTags

        self.reducedIntegrationPoints = None
        self.reducedIntegrationWeights = None
        self.reducedListOTags = None
        self.reducedEpsilonAtReducedIntegPoints = None
        self.dualReconstructionData = None


    def GetListOfTags(self):
        return self.listOfTags


    def GetNumberOfIntegrationPoints(self):
        return len(self.integrationWeights)


    def GetIntegrationWeights(self):
        return self.integrationWeights


    def GetGradPhiAtIntegPoint(self):
        return self.gradPhiAtIntegPoint



    def SetReducedIntegrationPoints(self, reducedIntegrationPoints):
        self.reducedIntegrationPoints = reducedIntegrationPoints


    def GetReducedIntegrationPoints(self):
        return self.reducedIntegrationPoints


    def SetReducedIntegrationWeights(self, reducedIntegrationWeights):
        self.reducedIntegrationWeights = reducedIntegrationWeights


    def GetReducedIntegrationWeights(self):
        return self.reducedIntegrationWeights


    def SetReducedListOTags(self, reducedListOTags):
        self.reducedListOTags = reducedListOTags


    def GetReducedListOTags(self):
        return self.reducedListOTags


    def SetReducedEpsilonAtReducedIntegPoints(self, reducedEpsilonAtReducedIntegPoints):
        self.reducedEpsilonAtReducedIntegPoints = reducedEpsilonAtReducedIntegPoints


    def GetReducedEpsilonAtReducedIntegPoints(self):
        return self.reducedEpsilonAtReducedIntegPoints


    def GetNumberOfSigmaComponents(self):
        return self.reducedEpsilonAtReducedIntegPoints.shape[0]


    def GetNumberOfReducedIntegrationPoints(self):
        return len(self.GetReducedIntegrationWeights())


    def GetNumberOfModes(self):
        return self.reducedEpsilonAtReducedIntegPoints.shape[2]


    def SetDualReconstructionData(self, dualReconstructionData):
        self.dualReconstructionData = dualReconstructionData


    def GetDualReconstructionData(self):
        return self.dualReconstructionData



    def __getstate__(self):

        state = {}
        state["listOfTags"] = None
        state["integrationWeights"] = None
        state["gradPhiAtIntegPoint"] = None

        state["reducedIntegrationPoints"] = self.reducedIntegrationPoints
        state["reducedIntegrationWeights"] = self.reducedIntegrationWeights
        state["reducedListOTags"] = self.reducedListOTags
        state["reducedEpsilonAtReducedIntegPoints"] = self.reducedEpsilonAtReducedIntegPoints
        state["dualReconstructionData"] = self.dualReconstructionData

        return state


    def __str__(self):
        res = "OperatorCompressionDataMechanical"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)



