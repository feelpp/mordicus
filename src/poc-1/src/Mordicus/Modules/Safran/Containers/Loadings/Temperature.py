# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
import numpy as np
import collections


class Temperature(LoadingBase):
    """

    Attributes
    ----------
    fieldsMap : collections.OrderedDict()
        dictionary with time indices (float) as keys and temperature fields tags (str) as values
    fields : dict
        dictionary with pressure vectors tags (str) keys and pressure vectors (np.ndarray of size (numberOfElementsInSet,)) as values
    fieldsAtReducedIntegrationPoints : np.ndarray
        np.ndarray of size (numberOfReducedIntegrationPoints) containing the temperature fields at reduced integration points
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(Temperature, self).__init__(set, "temperature")

        self.fieldsMap = collections.OrderedDict
        self.fields = {}
        self.fieldsAtReducedIntegrationPoints = {}


    def SetFieldsMap(self, fieldsMap):
        """
        Sets the fieldsMap attribute of the class

        Parameters
        ----------
        fieldsMap : collections.OrderedDict
        """
        # assert type of fieldsMap
        assert isinstance(fieldsMap, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(fieldsMap.keys())]
        )
        assert np.all([isinstance(key, str) for key in list(fieldsMap.values())])

        self.fieldsMap = fieldsMap

    def SetFields(self, fields):
        """
        Sets the fields attribute of the class

        Parameters
        ----------
        fields : dict
        """
        # assert type of fields
        assert isinstance(fields, dict)
        assert np.all([isinstance(key, str) for key in list(fields.keys())])
        assert np.all(
            [isinstance(value, np.ndarray) for value in list(fields.values())]
        )

        self.fields = fields



    def GetTemperatureAtReducedIntegrationPointsAtTime(self, time):
        """
        Computes the temperature at reduced integration points and at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        np.ndarray
            temperature at reduced integration points and at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI

        # compute fieldsAtReducedIntegrationPoints at time
        temperatureAtReducedIntegrationPoints = TI.PieceWiseLinearInterpolation(
            time,
            list(self.fieldsMap.keys()),
            self.fieldsAtReducedIntegrationPoints,
            list(self.fieldsMap.values()),
        )
        return temperatureAtReducedIntegrationPoints



    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, operatorCompressionData):

        assert isinstance(reducedOrderBasis, np.ndarray)
        assert 'reducedIntegrationPoints' in operatorCompressionData, "operatorCompressionData must contain a key 'reducedIntegrationPoints'"

        from Mordicus.Modules.Safran.FE import FETools as FT

        FEInterpAtIntegPointMatrix = FT.ComputeFEInterpMatAtGaussPoint(mesh)

        self.fieldsAtReducedIntegrationPoints = {}
        for key, field in self.fields.items():

            self.fieldsAtReducedIntegrationPoints[key] = FEInterpAtIntegPointMatrix.dot(field)[operatorCompressionData["reducedIntegrationPoints"]]




    def ComputeContributionToReducedExternalForces(self, time):
        """
        No contribution
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        return 0.


    def __getstate__(self):

        state = {}
        state["set"] = self.set
        state["type"] = self.type
        state["fieldsAtReducedIntegrationPoints"] = self.fieldsAtReducedIntegrationPoints
        state["fieldsMap"] = self.fieldsMap
        state["fields"] = {}
        for f in self.fields.keys():
            state["fields"][f] = None

        return state



    def __str__(self):
        res = "Temperature Loading with set "+self.GetSet()+"\n"
        res += "fieldsMap : "+str(self.fieldsMap)+"\n"
        res += "fields : "+str(self.fields)
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)