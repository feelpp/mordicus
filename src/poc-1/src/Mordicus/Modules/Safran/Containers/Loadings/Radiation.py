# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
import numpy as np
import collections


class Radiation(LoadingBase):
    """
    Class containing a Loading of type radiation

    Attributes
    ----------
    Text : collections.OrderedDict()
        dictionary with time indices (float) as keys and temporal Text (float) as values
    StefanBoltzmannConstant    : float
        the Stefan Boltzmann constant used for the boundary condition computation
    assembledReducedOrderBasisOnSet : numpy.ndarray
        size (numberOfModes)
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(Radiation, self).__init__(set, "radiation")

        self.StefanBoltzmannConstant = None
        self.Text = collections.OrderedDict
        self.assembledReducedOrderBasisOnSet = None


    def SetText(self, Text):
        """
        Sets the coeffients attribute of the class

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


    def GetTextAtTime(self, time):
        """
        Computes Text at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        float
            Text at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI

        # compute coefficient at time
        Text = TI.PieceWiseLinearInterpolation(
            time, list(self.Text.keys()), list(self.Text.values())
        )
        return Text



    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, operatorCompressionData):

        assert isinstance(reducedOrderBasis, np.ndarray)

        from Mordicus.Modules.Safran.FE import FETools as FT

        self.assembledReducedOrderBasisOnSet = FT.IntegrateOrderOneTensorOnSurface(mesh, self.set, reducedOrderBasis)



    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        Text = self.GetTextAtTime(time)

        return self.stefanBoltzmannConstant*(Text**4)*self.assembledReducedOrderBasisOnSet






    def __str__(self):
        res = "Radiation Loading with set "+self.GetSet()
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

