# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OperatorCompressionData.OperatorCompressionDataBase import OperatorCompressionDataBase



class OperatorCompressionDataMechanical(OperatorCompressionDataBase):
    """
    Class containing an OperatorCompressionDataMechanical, used in the
    operator compression step of the POD-ECM method. The implementation
    uses Lagrange isoparametric finite elements as high-dimension integration
    model.

    Attributes
    ----------
    gradPhiAtIntegPoint : scipy.sparse.coo_matrix
        of size (numberOfIntegrationPoints, numberOfModes), components of the
        gradient of the shape functions at the integration points
    integrationWeights : 1D np.ndarray
        of size (numberOfIntegrationPoints,), vector containing the integration
        weights associated to the computation of the internal forces vector
        with the high-fidelity integration scheme
    listOfTags : list of lists (of str)
        (of length numberOfIntegrationPoints) at each integration point,
        containing all the tags of the element containing the integration points
    reducedIntegrationPoints : 1D np.ndarray
        of size (numberOfReducedIntegrationPoints,), vector containing the
        of the integration points associated to the computation of the internal
        forces vector with the reduced integration scheme
    reducedIntegrationWeights : 1D np.ndarray
        of size (numberOfReducedIntegrationPoints,), vector containing the
        integration weights associated to the computation of the internal
        forces vector with the reduced integration scheme
    reducedListOTags : list of lists (of str)
        (of length numberOfReducedIntegrationPoints) at each reduced
        integration point containing all the tags of the element containing the
        reduced integration points. It is an extraction of listOfTags at the
        reduced integration points.
    reducedEpsilonAtReducedIntegPoints : np.ndarray
        of size (numberOfSigmaComponents,numberOfReducedIntegrationPoints,numberOfModes),
        dtype = float, containing :math:`\epsilon(\Psi)(x_k)` where :math:`\Psi`
        is a vector from the reducedOrderBasis associated to tje solution
        "U" and where :math:`x_k` are the reduced integration points
    dualReconstructionData: dict
        dictionary containing data used for reconstructing dual quantities
        in the online stage, with following key:values

        - "methodDualReconstruction" : str ("GappyPOD" or "MetaModel")

        - name of dual quantities (e.g. "evrcum"):

            - if "MetaModel" : tuple

                model: sklearn.model_selection._search.GridSearchCV

                scalerX: sklearn.preprocessing._data.StandardScaler

                scalery: sklearn.preprocessing._data.StandardScaler

            - if "GappyPOD" : tuple

                reducedOrderBasisAtReducedIntegrationPoints: np.ndarray of size (numberOfModes, nReducedIntegrationPoints)

    """

    def __init__(self, solutionName, gradPhiAtIntegPoint, integrationWeights, listOfTags):
        super(OperatorCompressionDataMechanical, self).__init__(solutionName)

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
        r"""
        Parameters
        ----------
        reducedEpsilonAtReducedIntegPoints: np.ndarray of size
            (numberOfSigmaComponents,numberOfReducedIntegrationPoints,numberOfModes),
            dtype = float
            contains :math:`\epsilon(\Psi)(x_k)` where :math:`\Psi` is a POD
            mode and :math:`x_k` are the reduced integration points
        """
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



