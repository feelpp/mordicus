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
import collections


class PressureBC(LoadingBase):
    """
    Class containing a Loading of type pressure boundary condition. A pressure vector over the elements of set at time t is given by : coefficients[ t ] * fields[ fieldsMap[ t ] ]


    Attributes
    ----------
    coefficients : collections.OrderedDict()
        dictionary with time indices (float) as keys and temporal coefficients (float) as values
    fieldsMap    : collections.OrderedDict()
        dictionary with time indices (float) as keys and pressure vectors tags (str) as values
    fields       : dict
        dictionary with pressure vectors tags (str) keys and pressure vectors (np.ndarray of size (numberOfElementsInSet,)) as values
    assembledReducedFields : dict
        dictionary with pressure vectors tags (str) keys and compressed pressure vectors (np.ndarray of size (numberOfModes,)) as values
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)
        assert solutionName == "U", "PressureBC loading can only be applied on U solution types"

        super(PressureBC, self).__init__("U", set, "pressure")

        #self.coefficients = collections.OrderedDict
        self.coefficientsTimes = None
        self.coefficientsValues = None        
        
        #self.fieldsMap = collections.OrderedDict
        self.fieldsMapTimes = None
        self.fieldsMapValues = None
        
        self.fields = {}
        self.assembledReducedFields = {}


    def SetCoefficients(self, coefficients):
        """
        Sets the coeffients attribute of the class

        Parameters
        ----------
        coefficients : collections.OrderedDict
        """
        # assert type of coefficients
        assert isinstance(coefficients, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(coefficients.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(coefficients.values())
            ]
        )

        #self.coefficients = coefficients
        self.coefficientsTimes = np.array(list(coefficients.keys()), dtype = float)
        self.coefficientsValues = np.array(list(coefficients.values()), dtype = float)        



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

        #self.fieldsMap = fieldsMap
        self.fieldsMapTimes = np.array(list(fieldsMap.keys()), dtype = float)
        self.fieldsMapValues = np.array(list(fieldsMap.values()), dtype = str)        



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



    def GetFields(self):
        return self.fields
    

    def GetAssembledReducedFieldAtTime(self, time):
        """
        Computes the pressure vector at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        np.ndarray
            pressure vector at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI

        # compute coefficient at time
        coefficient = TI.PieceWiseLinearInterpolation(
            time, self.coefficientsTimes, self.coefficientsValues
        )

        # compute vector field at time
        vectorField = TI.PieceWiseLinearInterpolationWithMap(
            time,
            self.fieldsMapTimes,
            self.assembledReducedFields,
            self.fieldsMapValues
        )

        return coefficient * vectorField



    def ReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):


        #AssembleLoadingAgainstReducedBasis

        from Mordicus.Modules.Safran.FE import FETools as FT


        self.assembledReducedFields = {}

        keymap = list(self.GetFields().keys())
        numberOfFields = len(keymap)
        
        
        fieldsAtIntegrationPoints = FT.CellDataToIntegrationPointsData(mesh, self.GetSet(), self.GetFields(), relativeDimension = -1)
        #this can be bypassed is the pressure values are already given at the integration points
        
        normalsAtIntegrationPoints = FT.ComputeNormalsAtIntegPoint(mesh, [self.GetSet()])

        integrationWeights, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh, [self.GetSet()], relativeDimension = -1)

        normalFieldsWeightsAtIntegrationPoints = np.einsum('ij,kj,j->jik', fieldsAtIntegrationPoints, normalsAtIntegrationPoints, integrationWeights, optimize = True)

        for f in range(numberOfFields):
            assembledField = phiAtIntegPoint.T.dot(normalFieldsWeightsAtIntegrationPoints[:,f,:]).T.flatten()
            
            self.assembledReducedFields[keymap[f]] = np.dot(reducedOrderBases[self.solutionName], assembledField)
            """assembledField0 = FT.IntegrateVectorNormalComponentOnSurface(mesh, self.GetSet(), self.GetFields()[keymap[f]])
            print("rel_dif =", np.linalg.norm(assembledField - assembledField0)/np.linalg.norm(assembledField0))"""



    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
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