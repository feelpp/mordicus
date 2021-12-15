# -*- coding: utf-8 -*-
import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase



class Temperature(LoadingBase):
    """

    Attributes
    ----------
    fieldsMap : dict
        dictionary with time indices (float) as keys and temperature fields tags (str) as values
    fields : dict
        dictionary with pressure vectors tags (str) keys and pressure vectors (np.ndarray of size (numberOfElementsInSet,)) as values
    fieldsAtReducedIntegrationPoints : np.ndarray
        np.ndarray of size (numberOfReducedIntegrationPoints) containing the temperature fields at reduced integration points
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)

        super(Temperature, self).__init__(solutionName, set, "temperature")


        #self.fieldsMap = dict
        self.fieldsMapTimes = None
        self.fieldsMapValues = None

        self.phiAtReducedIntegPoint = None

        self.fields = {}
        self.fieldsAtReducedIntegrationPoints = {}


    def SetFieldsMap(self, fieldsMapTimes, fieldsMapValues):
        """
        Sets the fieldsMap attribute of the class

        Parameters
        ----------
        fieldsMap : dict
        """
        # assert type of fieldsMap
        #assert isinstance(fieldsMap, dict)
        #assert np.all(
        #    [isinstance(key, (float, np.float64)) for key in list(fieldsMap.keys())]
        #)
        #assert np.all([isinstance(key, str) for key in list(fieldsMap.values())])

        #self.fieldsMap = fieldsMap
        self.fieldsMapTimes = fieldsMapTimes
        self.fieldsMapValues = fieldsMapValues


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
        assert np.all([isinstance(value, np.ndarray) for value in list(fields.values())])

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

        temperatureAtReducedIntegrationPoints = TI.PieceWiseLinearInterpolationWithMap(
            time,
            self.fieldsMapTimes,
            self.fieldsAtReducedIntegrationPoints,
            self.fieldsMapValues
        )
        return temperatureAtReducedIntegrationPoints


    def PreReduceLoading(self, mesh, operatorCompressionData):

        if self.phiAtReducedIntegPoint == None:

            assert 'reducedIntegrationPoints' in operatorCompressionData, "operatorCompressionData must contain a key 'reducedIntegrationPoints'"

            from Mordicus.Modules.Safran.FE import FETools as FT
            _, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh)
            self.phiAtReducedIntegPoint = phiAtIntegPoint.tocsr()[operatorCompressionData["reducedIntegrationPoints"],:]


    def ReduceLoading(self, mesh = None, problemData = None, reducedOrderBases = None, operatorCompressionData = None):

        self.PreReduceLoading(mesh, operatorCompressionData)

        self.fieldsAtReducedIntegrationPoints = {}
        for key, field in self.fields.items():

            self.fieldsAtReducedIntegrationPoints[key] = self.phiAtReducedIntegPoint.dot(field)


    def HyperReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):

        return



    def ComputeContributionToReducedExternalForces(self, time):
        """
        No contribution
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        return 0.


    def UpdateLoading(self, loading):


        self.SetFieldsMap(loading.fieldsMapTimes, loading.fieldsMapValues)
        self.SetFields(loading.fields)


    def __getstate__(self):

        state = {}
        state["solutionName"] = self.solutionName
        state["set"] = self.set
        state["type"] = self.type
        state["fieldsAtReducedIntegrationPoints"] = self.fieldsAtReducedIntegrationPoints
        state["fieldsMapTimes"] = self.fieldsMapTimes
        state["fieldsMapValues"] = self.fieldsMapValues
        state["phiAtReducedIntegPoint"] = self.phiAtReducedIntegPoint
        state["fields"] = {}
        for f in self.fields.keys():
            state["fields"][f] = None

        return state

    def __str__(self):
        res = "Temperature Loading with set "+self.GetSet()+"\n"
        res += "fieldsMapValues : "+str(self.fieldsMapValues)+"\n"
        #res += "fields : "+str(self.fields)
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)