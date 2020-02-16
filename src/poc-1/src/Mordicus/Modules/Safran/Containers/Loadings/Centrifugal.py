# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
import numpy as np
import collections


class Centrifugal(LoadingBase):
    """

    Attributes
    ----------
    rotationVelocity: collections.OrderedDict()
        dictionary with time indices (float) as keys and temporal coefficients (float) as values
    center    : np.ndarray
        np.ndarray of size 1, 2 or 3, containing the coordinates of the center of rotation
    direction : np.ndarray
        np.ndarray of size 1, 2 or 3, containing the unit vector of direction of rotation
    coefficient : float
        rotational velocity
    reducedUnitCentrifugalVector : np.ndarray
        np.ndarray of size (numberOfModes) containing the reducedUnitCentrifugalVector
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(Centrifugal, self).__init__(set, "centrifugal")

        self.rotationVelocity = collections.OrderedDict
        self.center = None
        self.direction = None
        self.coefficient = None
        self.reducedUnitCentrifugalVector = None


    def SetRotationVelocity(self, rotationVelocity):
        """
        Sets the coeffients attribute of the class

        Parameters
        ----------
        rotationVelocity : collections.OrderedDict
        """
        # assert type of rotationVelocity
        assert isinstance(rotationVelocity, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(rotationVelocity.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(rotationVelocity.values())
            ]
        )

        self.rotationVelocity = rotationVelocity


    def SetCenter(self, center):
        """
        1.
        """
        self.center = center


    def SetDirection(self, direction):
        """
        1.
        """
        self.direction = direction


    def SetCoefficient(self, coefficient):
        """
        1.
        """
        self.coefficient = coefficient


    def GetRotationVelocityAtTime(self, time):
        """
        Computes the rotationVelocity at time, using PieceWiseLinearInterpolation

        Parameters
        ----------
        time : float

        Returns
        -------
        float
            rotationVelocity at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI

        # compute rotationVelocity at time
        rotationVelocity = TI.PieceWiseLinearInterpolation(
            time, list(self.rotationVelocity.keys()), list(self.rotationVelocity.values())
        )
        return rotationVelocity




    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, operatorCompressionData):

        assert isinstance(reducedOrderBasis, np.ndarray)

        from Mordicus.Modules.Safran.FE import FETools as FT

        density = {}
        for set, law in problemData.GetConstitutiveLaws().items():
            density[set] = law.GetDensity()

        assembledUnitCentrifugalVector = FT.IntegrateCentrifugalEffect(mesh, density, self.direction, self.center)

        self.reducedUnitCentrifugalVector = np.dot(reducedOrderBasis, assembledUnitCentrifugalVector)



    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        rotationVelocity = self.GetRotationVelocityAtTime(time)

        return (self.coefficient*rotationVelocity)**2*self.reducedUnitCentrifugalVector




    def __str__(self):
        res = "Centrifugal Loading with set "+self.GetSet()+"\n"
        res += "rotationVelocity : "+str(self.rotationVelocity)+"\n"
        res += "center : "+str(self.center)+"\n"
        res += "direction : "+str(self.direction)
        return res
