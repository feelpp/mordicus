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
from Mordicus.Core.BasicAlgorithms import Interpolation as TI


class ConvectionHeatFlux(LoadingBase):
    """
    Class containing a Loading of type convection heat flux boundary condition
    for thermal problems.

    Attributes
    ----------
    hTimes : np.ndarray or list of floats
        time values on which heat transfert coefficient values are provided
    hValues : np.ndarray or list of floats
        heat transfert coefficient values at the corresponding time values
    TextTimes : np.ndarray or list of floats
        time values on which external temperature values are provided
    TextValues : np.ndarray or list of floats
        external temperature values at the corresponding time values

    reducedPhiT : numpy.ndarray
        of size (numberOfModes,) containing the precomputed vector
        "red" for deriving the convection heat flux reduced external forces
        contribution is the form: h*Text*red
    reducedPhiTPhiT : numpy.ndarray
        of size (numberOfModes, numberOfModes) containing the precomputed matrix
        "mat" for deriving the reduced global tangent matrix contribution
        is the form: h*mat
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)
        assert solutionName == "T", "ConvectionHeatFlux loading can only be applied on T solution types"

        super(ConvectionHeatFlux, self).__init__("T", set, "convection_heat_flux")

        self.hTimes = None
        self.hValues = None
        self.TextTimes = None
        self.TextValues = None

        self.reducedPhiT = None
        self.reducedPhiTPhiT = None


    def SetH(self, h):
        """
        Sets hTimes and hValues

        Parameters
        ----------
        h : dict
            dictionary with time steps (float) as keys and the values of the
            heat transfert coefficient (float)
        """
        # assert type of h
        assert isinstance(h, dict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(h.keys())])
        assert np.all([isinstance(key, (float, np.float64))
                for key in list(h.values())])

        self.hTimes = np.array(list(h.keys()), dtype = float)
        self.hValues = np.array(list(h.values()), dtype = float)


    def SetText(self, Text):
        """
        Sets TextTimes and TextValues

        Parameters
        ----------
        Text : dict
            dictionary with time steps (float) as keys and the values of the
            external temperature values (float)
        """
        # assert type of Text
        assert isinstance(Text, dict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(Text.keys())])
        assert np.all([isinstance(key, (float, np.float64))
                for key in list(Text.values())])

        self.TextTimes = np.array(list(Text.keys()), dtype = float)
        self.TextValues = np.array(list(Text.values()), dtype = float)


    def GetCoefficientsAtTime(self, time: float)-> (float, float):
        """
        Computes and return h and Text at time, using
        PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        float
            h at time
        float
            Text at time
        """
        h = TI.PieceWiseLinearInterpolation(time, self.hTimes, self.hValues)
        Text = TI.PieceWiseLinearInterpolation(time, self.TextTimes, self.TextValues)
        return h, Text


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

        integrationWeights, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh, [self.GetSet()], relativeDimension = -1)

        reducedPhiTAtIntegPoints = phiAtIntegPoint.dot(reducedOrderBases[self.solutionName].T)

        self.reducedPhiTPhiT = np.einsum('tk,tl,t->kl', reducedPhiTAtIntegPoints, reducedPhiTAtIntegPoints, integrationWeights, optimize = True)

        self.reducedPhiT = np.einsum('tk,t->k', reducedPhiTAtIntegPoints, integrationWeights, optimize = True)


    def ComputeContributionToReducedExternalForces(self, time):
        """
        Computes and returns the reduced external forces contribution of the
        loading

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

        h, Text = self.GetCoefficientsAtTime(time)

        return h*Text*self.reducedPhiT


    def __str__(self):
        res = "ConvectionHeatFlux Loading with set "+self.GetSet()
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

