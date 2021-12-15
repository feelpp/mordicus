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
from Mordicus.Core.BasicAlgorithms import Interpolation as TI


class Radiation(LoadingBase):
    """
    Class containing a Loading of type radiation

    Attributes
    ----------
    Text : dict
        dictionary with time indices (float) as keys and temporal Text (float) as values
    StefanBoltzmannConstant    : float
        the Stefan Boltzmann constant used for the boundary condition computation
    reducedPhiT : numpy.ndarray
        size (numberOfModes)
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)
        assert solutionName == "T", "Radiation loading can only be applied on T solution types"

        super(Radiation, self).__init__("T", set, "radiation")

        self.stefanBoltzmannConstant = 0.
        #self.Text = {}

        self.TextTimes = None
        self.TextValues = None

        self.reducedPhiT = None


    def SetText(self, Text):
        """
        Sets the coeffients attribute of the class

        Parameters
        ----------
        Text : dict
        """
        # assert type of Text
        assert isinstance(Text, dict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(Text.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(Text.values())
            ]
        )

        #self.Text = Text

        self.TextTimes = np.array(list(Text.keys()), dtype = float)
        self.TextValues = np.array(list(Text.values()), dtype = float)


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


    def GetTextAtTime(self, time: float)-> float:
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

        # compute coefficient at time
        Text = TI.PieceWiseLinearInterpolation(
            time, self.TextTimes, self.TextValues
        )
        return Text


    def ReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):

        from Mordicus.Modules.Safran.FE import FETools as FT


        integrationWeights, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh, [self.GetSet()], relativeDimension = -1)

        reducedPhiTAtIntegPoints = phiAtIntegPoint.dot(reducedOrderBases[self.solutionName].T)

        self.reducedPhiT = np.einsum('tk,t->k', reducedPhiTAtIntegPoints, integrationWeights, optimize = True)



    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))

        Text = self.GetTextAtTime(time)

        return self.stefanBoltzmannConstant*(Text**4)*self.reducedPhiT


    def __str__(self):
        res = "Radiation Loading with set "+self.GetSet()
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

