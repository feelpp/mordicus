# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OperatorCompressionData.OperatorCompressionDataBase import OperatorCompressionDataBase



class OperatorPreCompressionDataMechanical(OperatorCompressionDataBase):
    """
    Class containing an OperatorPreCompressionDataMechanical, used in a precomputation
    of the operator compression step of the POD-ECM method. The implementation
    uses Lagrange isoparametric finite elements as high-dimension integration
    model. This structure only depends on the mesh, and is computed once
    in nongeometrical varitions cases, even when snapshots are updated.

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
    """

    def __init__(self, solutionName, gradPhiAtIntegPoint, integrationWeights, listOfTags):
        super(OperatorPreCompressionDataMechanical, self).__init__(solutionName)

        self.gradPhiAtIntegPoint = gradPhiAtIntegPoint
        self.integrationWeights = integrationWeights
        self.listOfTags = listOfTags


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



    def __getstate__(self):

        state = {}
        state["listOfTags"] = None
        state["integrationWeights"] = None
        state["gradPhiAtIntegPoint"] = None

        return state


    def __str__(self):
        res = "OperatorPreCompressionDataMechanical"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)



