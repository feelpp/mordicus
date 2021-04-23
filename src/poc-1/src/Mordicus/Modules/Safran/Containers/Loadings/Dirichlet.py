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
#import collections


class Dirichlet(LoadingBase):
    """
    Class containing a Loading of type Dirichlet boundary condition.
    """

    def __init__(self, solutionName, set):
        assert isinstance(set, str)
        assert isinstance(solutionName, str)

        super(Dirichlet, self).__init__(solutionName, set, "dirichlet")

        self.function = ""
        self.assembledBC = None
        self.tgv = 1.e3  #(tres grande valeur) scalar used for penalisation


    def SetFunction(self, function):
        """
        Sets the function attribute of the class

        Parameters
        ----------
        function : function
        """
        self.function = function




    def GetAssembledReducedFieldAtTime(self, time):
        """
        1.
        """

        return self.assembledBC



    def ReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):


        from Mordicus.Modules.Safran.FE import FETools as FT
        integrationWeightsSet, phiAtIntegPointSet = FT.ComputePhiAtIntegPoint(mesh, [self.set], -1)

        numberOfNodes = mesh.GetNumberOfNodes()

        positionIntegPointsOnSet = phiAtIntegPointSet.dot(mesh.GetNodes())

        #print("mesh.GetNodes() =", mesh.GetNodes())
        numberOfComponents = reducedOrderBases[self.solutionName].shape[1]//numberOfNodes
        numberOfModes = reducedOrderBases[self.solutionName].shape[0]
        numberOfIntegrationPointsSet = phiAtIntegPointSet.shape[0]

        assert numberOfComponents == self.function(positionIntegPointsOnSet[0]).shape[0], 'dirichlet condition do not have the same number of components as the provided reducedOrderBasis'

        valueAtIntegPointSet = np.empty((numberOfIntegrationPointsSet,numberOfComponents))
        for i in range(numberOfIntegrationPointsSet):
            valueAtIntegPointSet[i,:] = self.function(positionIntegPointsOnSet[i])


        componentReducedOrderBasis = []
        for i in range(numberOfComponents):
            componentReducedOrderBasis.append(reducedOrderBases[self.solutionName][:,i*numberOfNodes:(i+1)*numberOfNodes].T)


        reducedPhiAtIntegPointSet = np.empty((numberOfComponents,numberOfIntegrationPointsSet,numberOfModes))

        for i in range(numberOfComponents):
            reducedPhiAtIntegPointSet[i] = phiAtIntegPointSet.dot(componentReducedOrderBasis[i])


        #print(np.einsum("ti,ti,t", valueAtIntegPointSet, valueAtIntegPointSet, integrationWeightsSet, optimize = True))
        #print(np.einsum("ti,itj,t->j", valueAtIntegPointSet, reducedPhiAtIntegPointSet, integrationWeightsSet, optimize = True))
        #1./0.
        self.assembledBC = np.einsum("ti,itj,t->j", valueAtIntegPointSet, reducedPhiAtIntegPointSet, integrationWeightsSet, optimize = True)



    def HyperReduceLoading(self, mesh, problemData, reducedOrderBases, operatorCompressionData):

        return



    def ComputeContributionToReducedExternalForces(self, time):
        """
        1.
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))


        return self.tgv*self.GetAssembledReducedFieldAtTime(time)



    def __getstate__(self):

        state = {}
        state["solutionName"] = self.solutionName
        state["set"] = self.set
        state["type"] = self.type
        state["function"] = self.function

        return state




    def __str__(self):
        res = "Dirichlet Loading with set "+self.GetSet()
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)