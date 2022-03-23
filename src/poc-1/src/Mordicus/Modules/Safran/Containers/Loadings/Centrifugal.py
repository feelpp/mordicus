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


class Centrifugal(LoadingBase):
    """
    Class containing a Loading of type centrifugal effects for mechanical
    problems.

    Attributes
    ----------
    rotationVelocityTimes: np.ndarray or list of floats
        time values on which rotation velocity values are provided
    rotationVelocityValues: np.ndarray or list of floats
        rotation velocity values at the corresponding time values

    center    : np.ndarray
        np.ndarray of size 1, 2 or 3, containing the coordinates of the center
        of rotation
    direction : np.ndarray
        np.ndarray of size 1, 2 or 3, containing the unit vector of direction
        of rotation
    coefficient : float
        coefficient multiplying the rotational velocity

    reducedUnitCentrifugalVector : np.ndarray
        np.ndarray of size (numberOfModes) containing the precomputed vector
        "red" for deriving the centrifugal reduced external forces contribution
        is the form: (coefficient*rotationVelocity)**2*red
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)
        assert solutionName == "U", "Centrifugal loading can only be applied on U solution types"

        super(Centrifugal, self).__init__("U", set, "centrifugal")

        self.rotationVelocityTimes = None
        self.rotationVelocityValues = None

        self.center = None
        self.direction = None
        self.coefficient = None

        self.reducedUnitCentrifugalVector = None

        #self.reducedIntegrationWeights = None
        #self.reducedIntegrationPoints = None
        #self.JdetAtReducedIntegPoint = None
        #self.reducedUnAssembledReducedUnitCentrifugalVector = None



    def SetRotationVelocity(self, rotationVelocity):
        """
        Sets rotationVelocityTimes and rotationVelocityValues

        Parameters
        ----------
        rotationVelocity : dict
            dictionary with time steps (float) as keys and the values of the
            rotation velocity (float)
        """
        # assert type of rotationVelocity
        assert isinstance(rotationVelocity, dict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(rotationVelocity.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(rotationVelocity.values())
            ]
        )

        self.rotationVelocityTimes = np.array(list(rotationVelocity.keys()), dtype = float)
        self.rotationVelocityValues = np.array(list(rotationVelocity.values()), dtype = float)


    def SetCenter(self, center):
        """
        Sets center

        Parameters
        ----------
        center : np.ndarray or list of floats
            coordinates of the center of rotation
        """
        self.center = np.array(center)


    def SetDirection(self, direction):
        """
        Sets direction

        Parameters
        ----------
        direction : np.ndarray or list of floats
            unit vector of direction of rotation
        """
        self.direction = np.array(direction)


    def SetCoefficient(self, coefficient):
        """
        Sets coefficient

        Parameters
        ----------
        coefficient : float
            coefficient multiplying the rotational velocity
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




    def ReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData = None):
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

        #density = {}
        #for key, law in problemData.GetConstitutiveLaws().items():
        #    if key[0] == "mechanical":
        #        density[key[1]] = law.GetDensity()
        #assembledUnitCentrifugalVector0 = FT.IntegrateCentrifugalEffect(mesh, density, self.direction, self.center)

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

        #densityRWeightAtIntegrationPoints = np.einsum('ij,i,i->ij', r, densityAtIntegrationPoints, integrationWeights, optimize = True)
        #assembledUnitCentrifugalVector = phiAtIntegPoint.T.dot(densityRWeightAtIntegrationPoints).T.flatten()
        #self.reducedUnitCentrifugalVector = np.dot(reducedOrderBases[self.solutionName], assembledUnitCentrifugalVector)

        numberOfComponents = mesh.GetDimensionality()
        numberOfIntegrationPoints = len(integrationWeights)
        numberOfModes = reducedOrderBases[self.solutionName].shape[0]
        numberOfNodes = mesh.GetNumberOfNodes()

        componentReducedOrderBasis = []
        for i in range(numberOfComponents):
            componentReducedOrderBasis.append(reducedOrderBases[self.solutionName][:,i*numberOfNodes:(i+1)*numberOfNodes].T)

        reducedPhiAtIntegPoints = np.empty((numberOfComponents,numberOfIntegrationPoints,numberOfModes))

        for i in range(numberOfComponents):
            reducedPhiAtIntegPoints[i] = phiAtIntegPoint.dot(componentReducedOrderBasis[i])

        #unAssembledReducedUnitCentrifugalVector = np.einsum('ij,i,jik->ik', r, densityAtIntegrationPoints, reducedPhiAtIntegPoints, optimize = True)
        #self.reducedUnitCentrifugalVector = np.einsum('ij,i->j', unAssembledReducedUnitCentrifugalVector, integrationWeights, optimize = True)

        #self.unAssembledReducedUnitCentrifugalVector = np.einsum('ij,i,jik->ki', r, densityAtIntegrationPoints, reducedPhiAtIntegPoints, optimize = True)

        unAssembledReducedUnitCentrifugalVector = np.einsum('ij,i,jik->ki', r, densityAtIntegrationPoints, reducedPhiAtIntegPoints, optimize = True)

        self.reducedUnitCentrifugalVector = np.dot(unAssembledReducedUnitCentrifugalVector, integrationWeights)

        #return unAssembledReducedUnitCentrifugalVector, integrationWeights



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

        rotationVelocity = self.GetRotationVelocityAtTime(time)

        return (self.coefficient*rotationVelocity)**2*self.reducedUnitCentrifugalVector



    def __getstate__(self):

        state = {}
        state["solutionName"] = self.solutionName
        state["set"] = self.set
        state["type"] = self.type
        state["rotationVelocityTimes"] = self.rotationVelocityTimes
        state["rotationVelocityValues"] = self.rotationVelocityValues
        state["center"] = self.center
        state["direction"] = self.direction
        state["coefficient"] = self.coefficient
        state["reducedUnitCentrifugalVector"] = self.reducedUnitCentrifugalVector

        #state["reducedIntegrationWeights"] = self.reducedIntegrationWeights
        #state["reducedIntegrationPoints"] = self.reducedIntegrationPoints
        #state["reducedUnAssembledReducedUnitCentrifugalVector"] = self.reducedUnAssembledReducedUnitCentrifugalVector
        #state["JdetAtReducedIntegPoint"] = self.JdetAtReducedIntegPoint


        return state

    def __str__(self):
        res = "Centrifugal Loading with set "+self.GetSet()+"\n"
        res += "rotationVelocityTimes  : "+str(self.rotationVelocityTimes)+"\n"
        res += "rotationVelocityValues : "+str(self.rotationVelocityValues)+"\n"
        res += "center                 : "+str(self.center)+"\n"
        res += "direction              : "+str(self.direction)+"\n"
        res += "coefficient            : "+str(self.coefficient)
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

