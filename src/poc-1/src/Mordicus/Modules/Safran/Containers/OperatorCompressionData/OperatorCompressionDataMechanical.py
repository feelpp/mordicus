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
    gradPhiAtIntegPoint : list
        of length dimensionality of the mesh, of scipy.sparse.coo_matrix of
        size (numberOfIntegrationPoints, numberOfModes), components of the
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
        dtype = float, containing :math:`\epsilon(\Psi)(x_k'')` where :math:`\Psi`
        is a vector from the reducedOrderBasis associated to tje solution
        "U" and where :math:`x_k'` are the reduced integration points
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

    def __init__(self, solutionName):
        super(OperatorCompressionDataMechanical, self).__init__(solutionName)

        self.gradPhiAtIntegPoint = None
        self.integrationWeights = None
        self.listOfTags = None

        self.reducedIntegrationPoints = None
        self.reducedIntegrationWeights = None
        self.reducedListOTags = None
        self.reducedEpsilonAtReducedIntegPoints = None
        self.dualReconstructionData = None


    def SetOperatorPreCompressionData(self, operatorPreCompressionDataMechanical):
        """
        Sets the gradPhiAtIntegPoint, integrationWeights and listOfTags
        attributes from an OperatorPreCompressionDataMechanical

        Parameters
        ----------
        operatorPreCompressionDataMechanical : OperatorPreCompressionDataMechanical
            data structure used in a precomputation of the operator compression step of the POD-ECM method
        """
        assert self.GetSolutionName() == operatorPreCompressionDataMechanical.GetSolutionName(), \
        "solutionName of operatorCompressionDataMechanical and operatorPreCompressionDataMechanical must be the same"
        self.gradPhiAtIntegPoint = operatorPreCompressionDataMechanical.GetGradPhiAtIntegPoint()
        self.integrationWeights = operatorPreCompressionDataMechanical.GetIntegrationWeights()
        self.listOfTags = operatorPreCompressionDataMechanical.GetListOfTags()


    def GetListOfTags(self):
        """
        Get the listOfTags attribute

        Returns
        -------
        list of lists (of str)
            (of length numberOfIntegrationPoints)
        """
        return self.listOfTags


    def GetIntegrationWeights(self):
        """
        Get the integrationWeights attribute

        Returns
        -------
        1D np.ndarray
            of size (numberOfIntegrationPoints,)
        """
        return self.integrationWeights


    def GetNumberOfIntegrationPoints(self):
        """
        Get the number of integration points

        Returns
        -------
        int
            number of integration points
        """
        return len(self.integrationWeights)


    def GetGradPhiAtIntegPoint(self):
        """
        Get the gradPhiAtIntegPoint attribute

        Returns
        -------
        list
            of length dimensionality of the mesh, of scipy.sparse.coo_matrix of
            size (numberOfIntegrationPoints, numberOfModes)
        """
        return self.gradPhiAtIntegPoint



    def SetReducedIntegrationPoints(self, reducedIntegrationPoints):
        """
        Sets the reducedIntegrationPoints attribute

        Parameters
        ----------
        reducedIntegrationPoints : 1D np.ndarray
            of size (numberOfReducedIntegrationPoints,)
        """
        self.reducedIntegrationPoints = reducedIntegrationPoints


    def GetReducedIntegrationPoints(self):
        """
        Get the reducedIntegrationPoints attribute

        Returns
        -------
        1D np.ndarray
            of size (numberOfReducedIntegrationPoints,)
        """
        return self.reducedIntegrationPoints


    def SetReducedIntegrationWeights(self, reducedIntegrationWeights):
        """
        Sets the reducedIntegrationWeights attribute

        Parameters
        ----------
        reducedIntegrationWeights : 1D np.ndarray
            of size (numberOfReducedIntegrationPoints,)
        """
        self.reducedIntegrationWeights = reducedIntegrationWeights


    def GetReducedIntegrationWeights(self):
        """
        Get the reducedIntegrationWeights attribute

        Returns
        -------
        1D np.ndarray
            of size (numberOfReducedIntegrationPoints,)
        """
        return self.reducedIntegrationWeights


    def SetReducedListOTags(self, reducedListOTags):
        """
        Sets the reducedListOTags attribute

        Parameters
        ----------
        reducedListOTags : list of lists (of str)
            (of length numberOfReducedIntegrationPoints) at each reduced
        """
        self.reducedListOTags = reducedListOTags


    def GetReducedListOTags(self):
        """
        Get the reducedListOTags attribute

        Returns
        -------
        list of lists (of str)
            (of length numberOfReducedIntegrationPoints)
        """
        return self.reducedListOTags


    def SetReducedEpsilonAtReducedIntegPoints(self, reducedEpsilonAtReducedIntegPoints):
        """
        Sets the reducedEpsilonAtReducedIntegPoints attribute

        Parameters
        ----------
        reducedEpsilonAtReducedIntegPoints : np.ndarray
            of size (numberOfSigmaComponents,numberOfReducedIntegrationPoints,numberOfModes)
        """
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
        """
        Get the number of second order tensor components

        Returns
        -------
        int
            number number of second order tensor components
        """
        return self.reducedEpsilonAtReducedIntegPoints.shape[0]


    def GetNumberOfReducedIntegrationPoints(self):
        """
        Get the number of reduced iontegration points

        Returns
        -------
        int
            number of reduced iontegration points
        """
        return len(self.GetReducedIntegrationWeights())


    def GetNumberOfModes(self):
        """
        Get the number of reducedOrderBasis modes

        Returns
        -------
        int
            number of reducedOrderBasis modes
        """
        return self.reducedEpsilonAtReducedIntegPoints.shape[2]


    def SetDualReconstructionData(self, dualReconstructionData):
        """
        Sets the dualReconstructionData attribute

        Parameters
        ----------
        dualReconstructionData: dict
            dictionary containing data used for reconstructing dual quantities
            in the online stage
        """
        self.dualReconstructionData = dualReconstructionData


    def GetDualReconstructionData(self):
        """
        Get the dualReconstructionData attribute

        Returns
        -------
        dict
            dictionary containing data used for reconstructing dual quantities
            in the online stage
        """
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



