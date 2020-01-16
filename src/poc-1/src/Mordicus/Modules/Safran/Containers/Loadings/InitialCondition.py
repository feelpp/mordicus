# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
import numpy as np


class InitialCondition(LoadingBase):
    """

    Attributes
    ----------
    type : string ("scalar" or "vector")
    
    data : float or np.ndarray of size (numberOfDofs,)
    
    reducedInitialCondition : np.ndarray of size (numberOfModes,)
    """

    def __init__(self, set):
        assert isinstance(set, str)
        
        super(InitialCondition, self).__init__(set, "initialCondition")

        self.type = ""
        self.data = None
        self.reducedInitialCondition = None


    def SetType(self, type):
        assert (type == "scalar" or type == "vector")

        self.type = type

    def SetData(self, data):

        self.data = data
        

    def SetReducedInitialCondition(self, reducedInitialCondition):

        self.reducedInitialCondition = reducedInitialCondition
        
        
    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, snapshotCorrelationOperator, operatorCompressionData):

        assert isinstance(reducedOrderBasis, np.ndarray)

        from Mordicus.Modules.Safran.FE import FETools as FT

        if self.type == "scalar":
            if self.data == 0.:
                self.SetReducedInitialCondition(np.zeros(reducedOrderBasis.shape[0]))
                return
            
            else:
                initVector = self.data * np.ones(reducedOrderBasis.shape[1])# pragma: no cover
        
        else:
            initVector = self.data# pragma: no cover

        self.SetReducedInitialCondition(np.dot(snapshotCorrelationOperator.dot(initVector),reducedOrderBasis))# pragma: no cover
            
    
    
    def ComputeContributionToReducedExternalForces(self, time):
        """
        No contribution
        """
        # assert type of time
        assert isinstance(time, (float, np.float64))
        
        return 0.
    

 
    def __getstate__(self):
        
        state = {}
        state["set"] = self.set
        state["type"] = self.type
        state["reducedInitialCondition"] = self.reducedInitialCondition
        state["data"] = None

        return state



    def __str__(self):
        res = "Initial Condition with set "+self.GetSet()+"\n"
        res += "type : "+str(self.type)
        return res
