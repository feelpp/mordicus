# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
import numpy as np
import collections


class Radiation(LoadingBase):
    """
    Class containing a Loading of type pressure boundary condition. A pressure vector over the elements of set at time t is given by : coefficients[ t ] * fields[ fieldsMap[ t ] ]


    Attributes
    ----------
    coefficients : collections.OrderedDict()
        dictionary with time indices (float) as keys and temporal coefficients (float) as values
    StefanBoltzmannConstant    : float
        the Stefan Boltzmann constant used for the boundary condition computation
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(Radiation, self).__init__(set, "radiation")

        self.StefanBoltzmannConstant = None
        self.coefficients = collections.OrderedDict


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

        self.coefficients = coefficients

    def SetStefanBoltzmannConstant(self, stefanBoltzmannConstant):
        """
        Sets the stefanBoltzmannConstant attribute of the class

        Parameters
        ----------
        stefanBoltzmannConstant : float
        """
        # assert type of stefanBoltzmannConstant
        assert isinstance(stefanBoltzmannConstant, (float, np.float64))

        self.stefanBoltzmannConstant = stefanBoltzmannConstant



    def GetCoefficientAtTime(self, time):
        """
        Computes the coefficient at time, using TimeInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        float
            coefficient at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import TimeInterpolation as TI

        # compute coefficient at time
        coefficient = TI.TimeInterpolation(
            time, list(self.coefficients.keys()), list(self.coefficients.values())
        )
        return coefficient



    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, snapshotCorrelationOperator, operatorCompressionData):

        return



    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        return #self.GetAssembledReducedFieldAtTime(time)






    def __str__(self):
        res = "Radiation Loading with set "+self.GetSet()
        return res
