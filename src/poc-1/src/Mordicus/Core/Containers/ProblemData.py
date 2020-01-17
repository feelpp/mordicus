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
    dataFolder : str
        name of the folder containing the data of the problemData, relative to the mordicus client script
    solutions : dict
        dictionary with solutionNames (str) as keys and solution (Solution) as values
    loadings : list
        dictionary with identifier (str) as keys and loading (LoadingBase) as values
    constitutiveLaws : dict
        dictionary with identifier (str) as keys and constitutive law (ConstitutiveLawBase) as values
    parameters : collections.OrderedDict
        dictionary with time indices as keys and a np.ndarray of size (parameterDimension,) containing the parameters
    """

    def __init__(self, dataFolder):
        """
        Parameters
        ----------
        dataFolder : str
        solutions : dict
        loadings : dict
        constitutiveLaws : dict
        parameters : collections.OrderedDict
        """
        self.dataFolder = dataFolder
        self.solutions = {}
        self.loadings = {}
        self.constitutiveLaws = {}
        self.parameters = collections.OrderedDict()


    def GetDataFolder(self):
        """
        Returns
        -------
        str
            dataFolder
        """
        return self.dataFolder


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
            )

        self.solutions[solution.GetSolutionName()] = solution


    def AddParameter(self, parameter, time = None):
        """
        Adds a parameter at time "time"

        Parameters
        ----------
        time : float, optional
            time of the snapshot, default: 0.
        parameter : np.ndarray
            of size (parameterDimension,)
        """

        assert isinstance(time, (float, np.float64, type(None)))
        assert type(parameter) == np.ndarray and len(parameter.shape) == 1

        if time == None:
            time = 0.

        if time in self.parameters:
            print(
                "Parameter at time "
                + str(time)
                + " already in parameters. Replacing it anyways."
            )
        else:
            self.parameters[time] = parameter


    def AddConstitutiveLaw(self, constitutiveLaw):
        """
        Adds a constitutive law or a list of constitutive laws to constitutiveLaws

        Parameters
        ----------
        constitutiveLaw : ConstitutiveLawBase
            the constitutive law of the problem for a given set and type
        """
        try:
            iter(constitutiveLaw)
        except TypeError:
            constitutiveLaw = [constitutiveLaw]
        for law in constitutiveLaw:
            if law.GetIdentifier() in self.constitutiveLaws:
                print(
                    "Solution "
                    + str(law.GetIdentifier())
                    + " already in problemData.loadings. Replacing it anyway."
                )  # pragma: no cover

            self.constitutiveLaws[law.GetIdentifier()] = law


    def AddLoading(self, loading):
        """
        Adds a loading or a list of loadings to loadings

        Parameters
        ----------
        loading : LoadingBase
            the loading of the problem for a given set and type
        """
        try:
            iter(loading)
        except TypeError:
            loading = [loading]
        for load in loading:
            if load.GetIdentifier() in self.loadings:
                print(
                    "Solution "
                    + str(load.GetIdentifier())
                    + " already in problemData.loadings. Replacing it anyway."
                )

            self.loadings[load.GetIdentifier()] = load


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
        dict
            loadings of the problem
        """
        return self.loadings



    def GetConstitutiveLaws(self):
        """
        Returns
        -------
        dict
            constitutive laws of the problem
        """
        return self.constitutiveLaws


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


    def CompressSolution(self, solutionName, snapshotCorrelationOperator, reducedOrderBasis):
        """
        Compress solutions of name "solutionName".

        Parameters
        ----------
        solutionName : str
            name of the solutions to compress
        snapshotCorrelationOperator : scipy.sparse.csr
            correlation operator between the snapshots
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """
        assert isinstance(solutionName, str)

        if solutionName not in self.solutions:
            raise (
                "You must provide solutions "
                + solutionName
                + "before trying to compress them"
            )  # pragma: no cover

        solution = self.GetSolution(solutionName)
        solution.CompressSnapshots(snapshotCorrelationOperator, reducedOrderBasis)



    def UncompressSolution(self, solutionName, reducedOrderBasis):
        """
        Uncompress solutions of name "solutionName".

        Parameters
        ----------
        solutionName : str
            name of the solutions to uncompress
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """
        assert isinstance(solutionName, str)

        if solutionName not in self.solutions:
            raise (
                "You must provide solutions "
                + solutionName
                + "before trying to compress them"
            )  # pragma: no cover

        solution = self.GetSolution(solutionName)
        solution.UncompressSnapshots(reducedOrderBasis)



    def __str__(self):
        res = "Solutions:" + str(list(self.solutions.keys()))
        return res
