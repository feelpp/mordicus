# -*- coding: utf-8 -*-
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
from Mordicus.Core.BasicAlgorithms import Interpolation as TI
import collections


class ConvectionHeatFlux(LoadingBase):
    """
    Class containing a Loading of type pressure boundary condition. A pressure vector over the elements of set at time t is given by : coefficients[ t ] * fields[ fieldsMap[ t ] ]


    Attributes
    ----------
    h : collections.OrderedDict()
        dictionary with time indices (float) as keys and h (float) as values
    Text    : collections.OrderedDict()
        dictionary with time indices (float) as keys and Text (str) as values
    assembledReducedOrderBasisOnSet : numpy.ndarray
        size (numberOfModes)
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(ConvectionHeatFlux, self).__init__(set, "convection_heat_flux")

        self.h = collections.OrderedDict
        self.Text = collections.OrderedDict

        self.hTimes = None
        self.hValues = None

        self.TextTimes = None
        self.TextValues = None

        self.assembledReducedOrderBasisOnSet = None
        self.assembledReducedOrderBasisOrderTwoOnSet = None


    def SetH(self, h):
        """
        Sets the coeffients attribute of the class

        Parameters
        ----------
        h : collections.OrderedDict
        """
        # assert type of h
        assert isinstance(h, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(h.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(h.values())
            ]
        )

        self.h = h

        self.hTimes = np.array(list(self.h.keys()), dtype = float)
        self.hValues = np.array(list(self.h.values()), dtype = float)



    def SetText(self, Text):
        """
        Sets the Text attribute of the class

        Parameters
        ----------
        Text : collections.OrderedDict
        """
        # assert type of Text
        assert isinstance(Text, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(Text.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(Text.values())
            ]
        )

        self.Text = Text

        self.TextTimes = np.array(list(self.Text.keys()), dtype = float)
        self.TextValues = np.array(list(self.Text.values()), dtype = float)


    def GetCoefficientsAtTime(self, time: float)-> (float, float):
        """
        Computes h and Text at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        float
            (h, Text) at time
        """

        h = TI.PieceWiseLinearInterpolation(
            time, self.hTimes, self.hValues
        )
        Text = TI.PieceWiseLinearInterpolation(
            time, self.TextTimes, self.TextValues
        )
        return h, Text




    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, operatorCompressionData):

        assert isinstance(reducedOrderBasis, np.ndarray)

        from Mordicus.Modules.Safran.FE import FETools as FT

        self.assembledReducedOrderBasisOnSet = FT.IntegrateOrderOneTensorOnSurface(mesh, self.set, reducedOrderBasis)

        self.assembledReducedOrderBasisOrderTwoOnSet = FT.IntegrateOrderTwoTensorOnSurface(mesh, self.set, reducedOrderBasis)





    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        h, Text = self.GetCoefficientsAtTime(time)

        return h*Text*self.assembledReducedOrderBasisOnSet




    def __str__(self):
        res = "ConvectionHeatFlux Loading with set "+self.GetSet()
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

