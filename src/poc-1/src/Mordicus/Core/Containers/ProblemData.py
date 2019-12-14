## -*- coding: utf-8 -*-

import numpy as np

from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers.Loadings import LoadingBase
import collections


class ProblemData(object):
    """
    Class containing a problemData

    Attributes
    ----------
    problemDataName : str
        name of the problem, a unique  (o good practice can be the folder containing the solutions, relative to the mordicus client script)
    solutions : dict
        dictionary with solutionNames (str) as keys and solution (Solution) as values
    loadings : list
        dictionary with identifier (str) as keys and loading (LoadingBase) as values
    parameters : collections.OrderedDict
        dictionary with time indices as keys and a np.ndarray of size (parameterDimension,) containing the parameters
    """

    def __init__(self, problemDataName):
        """
        Parameters
        ----------
        problemDataName : str
        solutions : dict
        loadings : list
        parameters : collections.OrderedDict
        """
        self.problemDataName = problemDataName
        self.solutions = {}
        self.loadings = {}
        self.parameters = collections.OrderedDict()


    def GetProblemDataName(self):
        """
        Returns
        -------
        str
            problemDataName
        """
        return self.problemDataName 
        

    def AddSolution(self, solution):
        """
        Adds a solution to solutions
        
        Parameters
        ----------
        solution : Solution
            the solution of the problem for a given field
        """
        assert isinstance(
            solution, Solution.Solution
        ), "solution must be an instance of Containers.Solution"

        if solution.GetSolutionName() in self.solutions:
            print(
                "Solution "
                + solution.solutionName
                + " already in problemData.solutions. Replacing it anyway."
            )  # pragma: no cover

        self.solutions[solution.GetSolutionName()] = solution

    def AddParameter(self, parameter, time=0.0):
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
        assert type(parameter) == np.ndarray and len(parameter.shape) == 1

        if time in self.parameters:
            print(
                "Parameter at time "
                + time
                + " already in parameters. Replacing it anyways."
            )  # pragma: no cover
        self.parameters[time] = parameter
        return

    def AddLoading(self, loading):
        """
        Adds a loading to loadings
        
        Parameters
        ----------
        loading : LoadingBase
            the loading of the problem for a given set and type
        """
        assert isinstance(
            loading, LoadingBase.LoadingBase
        ), "loading must be an instance of Containers.Loadings.LoadingBase"

        if loading.GetIdentifier() in self.solutions:
            print(
                "Solution "
                + loading.solutionName
                + " already in problemData.loadings. Replacing it anyway."
            )  # pragma: no cover

        self.solutions[loading.GetIdentifier()] = loading      


    def GetParameters(self):
        """
        Returns
        -------
        collections.OrderedDict()
            parameters
        """
        if self.parameters == False:
            raise (
                "Please initialize parameters before trying to retrieve them."
            )  # pragma: no cover
        return self.parameters
    

    def GetParametersTimeSequence(self):
        """
        Returns
        -------
        list
            list containing the time indices of the parameters
        """
        return list(self.parameters.keys())
        
        
    def GetParametersList(self):
        """
        Returns
        -------
        list
            list containing the parameters
        """
        return list(self.parameters.values())
    

    def GetParameterDimension(self):
        """
        Assert that the parameters have the same parameterDimension and return this size
        
        Returns
        -------
        int
            common parameterDimension
        """
        listParameterDimension = [
            parameter.shape[0] for _, parameter in self.GetParameters().items()
        ]
        assert listParameterDimension.count(listParameterDimension[0]) == len(
            listParameterDimension
        )
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
        from Mordicus.Core.BasicAlgorithms import TimeInterpolation as TI

        return TI.TimeInterpolation(
            time, list(self.parameters.keys()), list(self.parameters.values())
        )
        

    def GetLoadings(self):
        """
        Returns
        -------
        list
        """
        return self.loadings
        

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
    
    
    def DeleteHeavyData(self):
        """        
        Deletes Heavy Data from problemData structure
        """
        for s in self.solutions.values():
            s.DeleteHeavyData()

        for l in self.loadings.values():
            l.DeleteHeavyData() # pragma: no cover


    def __str__(self):
        res = "Solutions:" + str(list(self.solutions.keys()))
        return res
