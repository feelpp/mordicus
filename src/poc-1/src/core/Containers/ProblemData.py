## -*- coding: utf-8 -*-

import numpy as np

from core.Containers import Solution
from core.Containers.Loadings import LoadingBase
from core.Containers.BaseObject import BaseObject
import collections

class ProblemData(BaseObject):
    """
    Class containing a problemData

    Attributes
    ----------
    solutions : dict
        dictionary with solutionNames (str) as keys and solution (Solution) as values
    loadings : list
        list containing the loadings of the problem
    parameters : collections.OrderedDict()
        dictionary with time indices as keys and a np.ndarray of size (parameterDimension,) containing the parameters
    """

    def __init__(self):
        """
        Parameters
        ----------
        solutions : dict
        loadings : list
        parameters : collections.OrderedDict()
        """
        super(ProblemData,self).__init__()
        
        self.solutions  = {}
        self.loadings   = []
        self.parameters = collections.OrderedDict()
        
        

    def AddSolution(self, solution):
        """
        Adds a solution to solutions
        
        Parameters
        ----------
        solution : Solution
            the solution of the problem for a given field
        """   
        assert (isinstance(solution, Solution.Solution)), "solution must be an instance of an object inheriting from Containers.Solution"
        
        if solution.GetSolutionName() in self.solutions:
            print("Solution "+solution.solutionName+" already in problemData.solutions. Replacing it anyway.")  #pragma: no cover

        self.solutions[solution.GetSolutionName()] = solution  
        


    def AddParameter(self, parameter, time = 0.):
        """
        Adds a parameter at time "time"
        
        Parameters
        ----------
        time : float, optional
            time of the snapshot, default: 0.
        parameter : np.ndarray
            of size (parameterDimension,)
        """   
        
        assert isinstance(time, (float, np.float64))
        assert (type(parameter) == np.ndarray and len(parameter.shape) == 1)
        
        if time in self.parameters:
            print("Parameter at time "+time+" already in parameters. Replacing it anyways.") #pragma: no cover
        self.parameters[time] = parameter
        return 
    
    
    
    def GetParameters(self):
        """
        Returns
        -------
        collections.OrderedDict()
            parameters
        """
        if self.parameters == False:
            raise("Please initialize parameters before trying to retrieve them.") #pragma: no cover
        return self.parameters
    
    

    def GetParameterDimension(self):
        """
        Assert that the parameters have the same parameterDimension and return this size
        
        Returns
        -------
        int
            common parameterDimension
        """
        listParameterDimension = [parameter.shape[0] for _, parameter in self.GetParameters().items()]
        assert listParameterDimension.count(listParameterDimension[0]) == len(listParameterDimension) 
        return listParameterDimension[0]   
    


    def GetParameterAtTime(self, time):
        """
        Parameters
        ----------
        time : float
            time at which the parameter is retrieved
        
        Returns
        -------
        np.ndarray
            parameter
        """
        from core.BasicAlgorithms import TimeInterpolation as TI
        return TI.TimeInterpolation(time, list(self.parameters.keys()), list(self.parameters.values()))
    


    def SetLoadings(self, loadings):
        """
        Sets the loadings of the problem
        
        Parameters
        ----------
        loadings : list
        """        
        for loading in loadings:
            assert (isinstance(loading, LoadingBase.LoadingBase)), "all loadings must be instances of objects inheriting from Containers.LoadingBase"
        self.loadings = loadings
    


    def GetSolution(self, solutionName):
        """        
        Parameters
        ----------
        solutionName : str
            name of the solution to retrieve

        Returns
        -------
        Solution
        """
        return self.solutions[solutionName]



    def  __str__(self):
        res = "Solutions:"+str(list(self.solutions.keys()))
        return res
    
        

def CheckIntegrity():

    solution  = Solution.Solution("U", 2, 10, True)
    loading   = LoadingBase.LoadingBase()
    parameter = np.zeros(2)
    problemData = ProblemData()
    problemData.AddSolution(solution)
    problemData.SetLoadings([loading])
    problemData.GetSolution("U")
    problemData.AddParameter(parameter, 0.)
    problemData.GetParameterAtTime(0.)
    problemData.GetParameters()
    problemData.GetParameterDimension()
    print(problemData)
    return "ok"



if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
