# -*- coding: utf-8 -*-
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
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

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)
        assert solutionName == "U", "Centrifugal loading can only be applied on U solution types"
        

        super(Centrifugal, self).__init__("U", set, "centrifugal")

        #self.rotationVelocity = collections.OrderedDict
        
        self.rotationVelocityTimes = None
        self.rotationVelocityValues = None
        
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

        #self.rotationVelocity = rotationVelocity
        
        self.rotationVelocityTimes = np.array(list(rotationVelocity.keys()), dtype = float)
        self.rotationVelocityValues = np.array(list(rotationVelocity.values()), dtype = float)


    def SetCenter(self, center):
        """
        1.
        """
        self.center = np.array(center)


    def SetDirection(self, direction):
        """
        1.
        """
        self.direction = np.array(direction)


    def SetCoefficient(self, coefficient):
        """
        1.
        """
        self.coefficient = coefficient


    def GetRotationVelocityAtTime(self, time: float)-> float:
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
            time, self.rotationVelocityTimes, self.rotationVelocityValues
        )
        
        return rotationVelocity




    def ReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):

        from Mordicus.Modules.Safran.FE import FETools as FT

        """density = {}
        for key, law in problemData.GetConstitutiveLaws().items():
            if key[0] == "mechanical":
                density[key[1]] = law.GetDensity()
                
        assembledUnitCentrifugalVector0 = FT.IntegrateCentrifugalEffect(mesh, density, self.direction, self.center)"""

        
        integrationWeights, phiAtIntegPoint = FT.ComputePhiAtIntegPoint(mesh)
        integrationPointsPosition = phiAtIntegPoint.dot(mesh.GetNodes())
        ipPositionFromRotationCenter = integrationPointsPosition - self.center
        length = np.einsum('ij,j->i', ipPositionFromRotationCenter, self.direction, optimize = True)        
        ipProjectionFromRotationCenter = np.outer(length, np.array(self.direction))        
        r = (ipPositionFromRotationCenter - ipProjectionFromRotationCenter)
        
        integrationPointsTags = FT.ComputeIntegrationPointsTags(mesh)        
        assert len(integrationPointsTags) == len(integrationWeights), "integrationPointsTags and integrationWeights have different length"
        constitutiveLawSets = problemData.GetSetsOfConstitutiveOfType("mechanical")        
        materialKeyPerIntegrationPoint = FT.ComputeMaterialKeyPerIntegrationPoint(integrationPointsTags, constitutiveLawSets)
        
        densityAtIntegrationPoints = np.array([problemData.GetConstitutiveLaws()[("mechanical",set)].GetDensity() for set in materialKeyPerIntegrationPoint])
                
        densityRWeightAtIntegrationPoints = np.einsum('ij,i,i->ij', r, densityAtIntegrationPoints, integrationWeights, optimize = True)

        assembledUnitCentrifugalVector = phiAtIntegPoint.T.dot(densityRWeightAtIntegrationPoints).T.flatten()
        
        self.reducedUnitCentrifugalVector = np.dot(reducedOrderBases[self.solutionName], assembledUnitCentrifugalVector)



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
        res += "rotationVelocityTimes : "+str(self.rotationVelocityTimes)+"\n"
        res += "rotationVelocityValues : "+str(self.rotationVelocityValues)+"\n"
        res += "center : "+str(self.center)+"\n"
        res += "direction : "+str(self.direction)
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

