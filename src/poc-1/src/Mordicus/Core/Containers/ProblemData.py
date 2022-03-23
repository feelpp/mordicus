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
from scipy import sparse

from Mordicus.Core.Containers import Solution


class ProblemData(object):
    """
    Class containing a problemData

    Attributes
    ----------
    problemName : str
        name of the ProblemData object
    dataFolder : str
        name of folder containing the data of the problemData, relative to the mordicus client script
    solutions : dict
        dictionary with solutionNames (str) as keys and solution (Solution) as values
    initialCondition : InitialConditionBase
        initial condition of the problem
    loadings : list
        dictionary with identifier (str) as keys and loading (LoadingBase) as values
    constitutiveLaws : dict
        dictionary with identifier (str) as keys and constitutive law (ConstitutiveLawBase) as values
    parameters : dict
        dictionary with time indices as keys and a np.ndarray of size (parameterDimension,) containing the parameters
    """

    def __init__(self, problemName):

        self.problemName = problemName
        self.dataFolder = None
        self.solutions = {}
        self.initialCondition = None
        self.loadings = {}
        self.constitutiveLaws = {}
        self.parameters = {}


    def SetDataFolder(self, dataFolder):
        """
        Sets the dataFolder parameter

        Parameters
        ----------
        dataFolder : str
            name of folder containing the data of the problemData, relative to the mordicus client script
        """
        self.dataFolder = dataFolder


    def GetDataFolder(self):
        """
        Returns the dataFolder parameter

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



    def DeleteSolutions(self):
        """
        Reinitializes the solutions parameter
        """
        self.solutions = {}


    def AddParameter(self, parameter, time = 0.):
        """
        Adds a parameter at time "time"

        Parameters
        ----------
        parameter : np.ndarray
            of size (parameterDimension,)
        time : float
            (optional) time of the snapshot, default: 0.
        """
        assert type(parameter) == np.ndarray and len(parameter.shape) == 1
        time = float(time)

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
                    "ConstitutiveLaw "
                    + str(law.GetIdentifier())
                    + " already in problemData.constitutiveLaws. Replacing it anyway."
                )  # pragma: no cover

            self.constitutiveLaws[law.GetIdentifier()] = law


    def SetInitialCondition(self, initialCondition):
        """
        Sets the initial condition

        Parameters
        ----------
        initialCondition : InitialCondition
            initial condition of the problem
        """
        self.initialCondition = initialCondition


    def GetInitialCondition(self):
        """
        Returns the initial condition

        Returns
        -------
        initialCondition : InitialCondition
            initial condition of the problem
        """
        return self.initialCondition



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
                    "Loading "
                    + str(load.GetIdentifier())
                    + " already in problemData.loadings. Replacing it anyway."
                )

            self.loadings[load.GetIdentifier()] = load


    def UpdateLoading(self, loading):
        """
        Update a loading or a list of loadings to loadings

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
            if load.GetIdentifier() not in self.loadings: # pragma: no cover
                print(
                    "Loading "
                    + str(load.GetIdentifier())
                    + " not present in problemData.loadings. Cannot update."
                )

            self.loadings[load.GetIdentifier()].UpdateLoading(load)


    def GetParameters(self):
        """
        Returns the parameters

        Returns
        -------
        dict
            parameters
        """
        if self.parameters == False:
            raise AttributeError(
                "Please initialize parameters before trying to retrieve them."
            )  # pragma: no cover
        return self.parameters


    def GetParametersTimeSequence(self):
        """
        Returns the time indices of the parameters

        Returns
        -------
        list
            list containing the time indices of the parameters
        """
        return list(self.parameters.keys())


    def GetParametersList(self):
        """
        Returns the parameter values in the form of a list

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
        int or None
            common parameterDimension
        """
        listParameterDimension = [
            parameter.shape[0] for _, parameter in self.GetParameters().items()
        ]
        if len(listParameterDimension)>0:
            assert listParameterDimension.count(listParameterDimension[0]) == len(
                listParameterDimension
            )
            return listParameterDimension[0]
        else:# pragma: no cover
            return None


    def GetParameterAtTime(self, time):
        """
        Returns the parameter value at a specitiy time (with time interpolation if needed)

        Parameters
        ----------
        time : float
            time at which the parameter is retrieved

        Returns
        -------
        np.ndarray
            parameter
        """

        from Mordicus.Core.BasicAlgorithms import Interpolation as TI
        return TI.PieceWiseLinearInterpolation(
        time, list(self.parameters.keys()), list(self.parameters.values())
        )
        #return self.parameters[time]


    def GetLoadings(self):
        """
        Returns the complete loadings dictionary

        Returns
        -------
        dict
            loadings of the problem
        """
        return self.loadings



    def GetLoading(self, solutionName, type, set):
        """
        Returns a specific loading for the identifiers elements

        Returns
        -------
        loading
        """
        for loading in self.GetLoadings().values():
            if loading.GetIdentifier() == (solutionName,type,set):
                return loading
        else:# pragma: no cover
            raise("loading "+str((solutionName, type, set))+" not available")


    def GetLoadingsOfType(self, type):
        """
        Returns all loadings of a specific type, in a list

        Returns
        -------
        list
            list of loadings of type type
        """
        li = []
        for loading in self.GetLoadings().values():
            if loading.GetType() == type:
                li.append(loading)# pragma: no cover
        return li


    def GetLoadingsForSolution(self, solutionName):
        """
        Returns all loadings for a specific solution name, in a list

        Returns
        -------
        list
            list of loadings of type type
        """
        li = []
        for loading in self.GetLoadings().values():
            if loading.GetSolutionName() == solutionName:
                li.append(loading)# pragma: no cover
        return li


    def GetConstitutiveLaws(self):
        """
        Returns the complete constitutiveLaws dictionary

        Returns
        -------
        dict
            constitutive laws of the problem
        """
        return self.constitutiveLaws


    def GetConstitutiveLawsOfType(self, type):
        """
        Returns all constitutive laws of a specific type, in a list

        Returns
        -------
        list
            list of constitutive laws of type type
        """
        li = []
        for law in self.GetConstitutiveLaws().values():
            if law.GetType() == type:
                li.append(law)# pragma: no cover
        return li


    def GetSetsOfConstitutiveOfType(self, type):
        """
        Returns the sets of all constitutive laws of a specific type, in a set

        Returns
        -------
        set
            set of strings of elementSets
        """
        se = []
        for law in self.GetConstitutiveLawsOfType(type):
            se.append(law.GetSet())
        return set(se)


    def GetSolution(self, solutionName):
        """
        Returns the solution of name solutionName

        Parameters
        ----------
        solutionName : str
            name of the solution to retrieve

        Returns
        -------
        Solution
        """
        return self.solutions[solutionName]


    def GetSolutions(self):
        """
        Returns the solutions of problemData

        Returns
        -------
        dict
            solutions
        """
        return self.solutions


    def CompressSolution(self, solutionName, reducedOrderBasis, snapshotCorrelationOperator = None):
        """
        Compress solutions of name solutionName ; does nothing if no solution of name solutionName exists

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

        if snapshotCorrelationOperator is None:
            snapshotCorrelationOperator = sparse.eye(self.GetSolution(solutionName).GetNumberOfDofs())

        try:
            solution = self.GetSolution(solutionName)
            solution.CompressSnapshots(snapshotCorrelationOperator, reducedOrderBasis)
        except KeyError:#pragma: no cover
            return


    def ConvertCompressedSnapshotReducedOrderBasis(self, solutionName, projectedReducedOrderBasis):
        """
        Converts the reducedSnapshot from the current reducedOrderBasis to a newReducedOrderBasis using a projectedReducedOrderBasis between the current one and a new one

        Parameters
        ----------
        solutionName : str
            name of the solution whose compressedSnapshot is to convert
        projectedReducedOrderBasis : np.ndarray
            of size (newNumberOfModes, numberOfModes)
        """
        solution = self.GetSolution(solutionName)
        solution.ConvertCompressedSnapshotReducedOrderBasis(projectedReducedOrderBasis)


    def UncompressSolution(self, solutionName, reducedOrderBasis):
        """
        Uncompress solutions of name solutionName

        Parameters
        ----------
        solutionName : str
            name of the solutions to uncompress
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """
        assert isinstance(solutionName, str)

        if solutionName not in self.solutions:
            raise AttributeError(
                "You must provide solutions "
                + solutionName
                + " before trying to uncompress them"
            )  # pragma: no cover

        solution = self.GetSolution(solutionName)
        solution.UncompressSnapshots(reducedOrderBasis)

    def accept(self, visitor):
        """
        Accept Visitor
        """
        return visitor.visitProblemData(self)

    def __str__(self):
        res = "ProblemData of name: "+self.problemName
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


