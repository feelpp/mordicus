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

class PressureBC(LoadingBase):
    """
    Class containing a Loading of type pressure boundary condition for
    mechanical problems.
    A pressure vector over the elements of set at time t is given by :
    coefficients[ t ] * fields[ fieldsMap[ t ] ]

    Attributes
    ----------
    coefficientsTimes : np.ndarray or list of floats
        time values on which coefficient values are provided
    coefficientsValues : np.ndarray or list of floats
        coefficient values at the corresponding time values

    fieldsMapTimes : np.ndarray or list of floats
        time values on which filed maps values are provided
    fieldsMapValues : np.ndarray or list of str
        filed maps values at the corresponding time values
    fields : dict
        dictionary with pressure vectors tags (str) keys and pressure vectors
        (np.ndarray of size (numberOfElementsInSet,)) as values

    assembledReducedFields : dict
        dictionary with pressure vectors tags (str) keys and compressed
        pressure vectors (np.ndarray of size (numberOfModes,)) as values.
        The pressure reduced external forces contribution is in the form:
        h*Text*red, where red is obtained by time interpolation over values of
        assembledReducedFields
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)
        assert solutionName == "U", "PressureBC loading can only be applied on U solution types"

        super(PressureBC, self).__init__("U", set, "pressure")

        self.coefficientsTimes = None
        self.coefficientsValues = None

        self.fieldsMapTimes = None
        self.fieldsMapValues = None
        self.fields = {}

        self.assembledReducedFields = {}


    def SetCoefficients(self, coefficients):
        """
        Sets coefficientsTimes and coefficientsValues

        Parameters
        ----------
        coefficients : dict
            dictionary with time steps (float) as keys and the values of the
            coefficient (float)
        """
        # assert type of coefficients
        assert isinstance(coefficients, dict)
        assert np.all([isinstance(key, (float, np.float64))
                       for key in list(coefficients.keys())])
        assert np.all([isinstance(key, (float, np.float64))
                for key in list(coefficients.values())])

        self.coefficientsTimes = np.array(list(coefficients.keys()), dtype = float)
        self.coefficientsValues = np.array(list(coefficients.values()), dtype = float)


    def SetFieldsMap(self, fieldsMap):
        """
        Sets fieldsMapTimes and fieldsMapValues

        Parameters
        ----------
        fieldsMap : dict
            dictionary with time steps (float) as keys and the filed maps
            values (str)
        """
        # assert type of fieldsMap
        assert isinstance(fieldsMap, dict)
        assert np.all([isinstance(key, (float, np.float64))
                       for key in list(fieldsMap.keys())])
        assert np.all([isinstance(key, str) for key in list(fieldsMap.values())])

        self.fieldsMapTimes = np.array(list(fieldsMap.keys()), dtype = float)
        self.fieldsMapValues = np.array(list(fieldsMap.values()), dtype = str)


    def SetFields(self, fields):
        """
        Sets fields

        Parameters
        ----------
        fields : dict
            dictionary with pressure vectors tags (str) keys and pressure
            vectors (np.ndarray of size (numberOfElementsInSet,)) as values
        """
        # assert type of fields
        assert isinstance(fields, dict)
        assert np.all([isinstance(key, str) for key in list(fields.keys())])
        assert np.all([isinstance(value, np.ndarray)
                       for value in list(fields.values())])

        self.fields = fields


    def GetFields(self):
        """
        Returns the complete field dictionary

        Returns
        -------
        dict
            dictionary with pressure vectors tags (str) keys and pressure vectors
            (np.ndarray of size (numberOfElementsInSet,)) as values
        """
        return self.fields


    def GetAssembledReducedFieldAtTime(self, time):
        """
        Computes and returns the pressure vector at time, using
        PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        np.ndarray
            of size (numberOfElementsInSet,), pressure vector at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI

        # compute coefficient at time
        coefficient = TI.PieceWiseLinearInterpolation(time,
                              self.coefficientsTimes, self.coefficientsValues)

        # compute vector field at time
        vectorField = TI.PieceWiseLinearInterpolationWithMap(
            time,
            self.fieldsMapTimes,
            self.assembledReducedFields,
            self.fieldsMapValues)

        return coefficient * vectorField



    def ReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):
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
            not used in this loading
            dictionary with solutionNames (str) as keys and data structure
            generated by the operator compression step as values
        """
        from Mordicus.Modules.Safran.FE import FETools as FT

        self.assembledReducedFields = {}

        keymap = list(self.GetFields().keys())
        numberOfFields = len(keymap)

        fieldsAtIntegrationPoints = FT.CellDataToIntegrationPointsData(mesh, self.GetFields(), self.GetSet(), relativeDimension = -1)
        #this can be bypassed is the pressure values are already given at the integration points

        normalsAtIntegrationPoints = FT.ComputeNormalsAtIntegPoint(mesh, [self.GetSet()])

        integrationWeights, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh, [self.GetSet()], relativeDimension = -1)

        normalFieldsWeightsAtIntegrationPoints = np.einsum('ij,kj,j->jik', fieldsAtIntegrationPoints, normalsAtIntegrationPoints, integrationWeights, optimize = True)

        for f in range(numberOfFields):
            assembledField = phiAtIntegPoint.T.dot(normalFieldsWeightsAtIntegrationPoints[:,f,:]).T.flatten()

            self.assembledReducedFields[keymap[f]] = np.dot(reducedOrderBases[self.solutionName], assembledField)
            """assembledField0 = FT.IntegrateVectorNormalComponentOnSurface(mesh, self.GetSet(), self.GetFields()[keymap[f]])
            print("rel_dif =", np.linalg.norm(assembledField - assembledField0)/np.linalg.norm(assembledField0))"""


    #def HyperReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):
    #    return


    def ComputeContributionToReducedExternalForces(self, time):
        """
        Computes and returns the reduced external forces contribution of the loading

        Parameters
        ----------
        time : float

        Returns
        -------
        np.ndarray
            of size (numberOfModes,)
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        return self.GetAssembledReducedFieldAtTime(time)


    def __getstate__(self):

        state = {}
        state["solutionName"] = self.solutionName
        state["set"] = self.set
        state["type"] = self.type
        state["coefficientsTimes"] = self.coefficientsTimes
        state["coefficientsValues"] = self.coefficientsValues
        state["fieldsMapTimes"] = self.fieldsMapTimes
        state["fieldsMapValues"] = self.fieldsMapValues
        state["assembledReducedFields"] = self.assembledReducedFields
        state["fields"] = {}
        for f in self.fields.keys():
            state["fields"][f] = None

        return state


    def __str__(self):
        res = "Pressure Loading with set "+self.GetSet()
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)