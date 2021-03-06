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
from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase


class Temperature(LoadingBase):
    """
    Class containing a Loading of type temperature for mechanical problems.

    Attributes
    ----------
    fieldsMapTimes : np.ndarray or list of floats
        time values on which filed maps values are provided
    fieldsMapValues : np.ndarray or list of str
        filed maps values at the corresponding time values
    fields : dict
        dictionary with temperature vectors tags (str) keys and temperature
        vectors (np.ndarray of size (numberOfNodes,)) at integration
        points as values
    fieldsAtReducedIntegrationPoints : dict
        dictionary with temperature vectors tags (str) keys and temperature
        vectors (np.ndarray of size (numberOfReducedIntegPoints,)) at reduced
        integration points as values

    phiAtReducedIntegPoint : scipy.sparse matrix
        of size (numberOfReducedIntegPoints,numberOfNodes) containing the
        finite element basis functions evaluated at the reduced integration
        points, so that the temperature fields at reduced integration points
        are obtained by phiAtReducedIntegPoint.dot(field)
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)

        super(Temperature, self).__init__(solutionName, set, "temperature")

        self.fieldsMapTimes = None
        self.fieldsMapValues = None
        self.fields = {}
        self.fieldsAtReducedIntegrationPoints = {}

        self.phiAtReducedIntegPoint = None


    def SetFieldsMap(self, fieldsMapTimes, fieldsMapValues):
        """
        Sets fieldsMapTimes and fieldsMapValues

        Parameters
        ----------
        fieldsMapTimes : np.ndarray or list of floats
            time values on which filed maps values are provided
            fieldsMapValues : np.ndarray or list of str
            filed maps values at the corresponding time values
        """
        self.fieldsMapTimes = fieldsMapTimes
        self.fieldsMapValues = fieldsMapValues


    def SetFields(self, fields):
        """
        Sets fields

        Parameters
        ----------
        fields : dict
            dictionary with temperature vectors tags (str) keys and temperature
            vectors (np.ndarray of size (numberOfNodes,)) at integration
            points as values
        """
        # assert type of fields
        assert isinstance(fields, dict)
        assert np.all([isinstance(key, str) for key in list(fields.keys())])
        assert np.all([isinstance(value, np.ndarray)
                       for value in list(fields.values())])

        self.fields = fields


    def GetTemperatureAtReducedIntegrationPointsAtTime(self, time):
        """
        Computes and returns the temperature at reduced integration points and
        at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        np.ndarray
            of size (numberOfReducedIntegPoints,), temperature at reduced
            integration points and at time
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


    def GetTemperatureAtTime(self, time):
        """
        Computes and returns the temperature at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        np.ndarray
            of size (numberOfNodes,), temperature at nodes and at time
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI

        # compute fields at time
        temperature = TI.PieceWiseLinearInterpolationWithMap(
            time,
            self.fieldsMapTimes,
            self.fields,
            self.fieldsMapValues
        )
        return temperature


    def PreReduceLoading(self, mesh, operatorCompressionData):
        """
        Prepares ReduceLoading by setting phiAtReducedIntegPoint

        Parameters
        ----------
        mesh : BasicTools.Containers.UnstructuredMesh
            mesh of the high-fidelity model
        operatorCompressionData : OperatorCompressionDataMechanical
            data structure generated by the operator compression for Mechanical
            problems
        """

        if self.phiAtReducedIntegPoint == None:

            from Mordicus.Modules.Safran.FE import FETools as FT
            _, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh)
            self.phiAtReducedIntegPoint = phiAtIntegPoint.tocsr()[operatorCompressionData.GetReducedIntegrationPoints(),:]


    def ReduceLoading(self, mesh = None, problemData = None, reducedOrderBases = None, operatorCompressionData = None):
        """
        Computes and sets the reduced representation of the loading

        Parameters
        ----------
        mesh : BasicTools.Containers.UnstructuredMesh
            mesh of the high-fidelity model
        problemData : ProblemData
            problemData containing the loading
        reducedOrderBases : dict(str: np.ndarray)
            dictionary with solutionNames (str) as keys and reducedOrderBases
            (np.ndarray of size (numberOfModes, numberOfDOFs)) as values
        operatorCompressionData : dict(str: custom_data_structure)
            dictionary with solutionNames (str) as keys and data structure
            generated by the operator compression step as values
        """
        self.PreReduceLoading(mesh, operatorCompressionData)

        self.fieldsAtReducedIntegrationPoints = {}
        for key, field in self.fields.items():

            self.fieldsAtReducedIntegrationPoints[key] = self.phiAtReducedIntegPoint.dot(field)


    #def HyperReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):
    #    return


    def ComputeContributionToReducedExternalForces(self, time):
        """
        Computes and returns the reduced external forces contribution of the
        loading, which is zero for temperature loadings

        Parameters
        ----------
        time : float

        Returns
        -------
        0.
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        return 0.


    def UpdateLoading(self, loading):
        """
        Update the high-dimensional data of the temperature loading, from
        another temperature loading

        Parameters
        ----------
        loading : Temperature
        """
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