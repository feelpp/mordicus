# -*- coding: utf-8 -*-

import numpy as np
import pickle
from scipy import sparse
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import Solution
from mpi4py import MPI

class CollectionProblemData(object):
    """
    Class containing a set of collection of problemData

    Attributes
    ----------
    problemDatas : dict
        dictionary with problem tags (str) as keys and problemDatas (ProblemData) as values
    reducedOrderBases : dict
        dictionary with solutionNames (str) as keys and reducedOrderBases (np.ndarray of size (numberOfModes, numberOfDOFs)) as values
    snapshotCorrelationOperators : dict
        dictionary with solutionNames (str) as keys and matrices (scipy.sparse.csr) as values
    operatorCompressionData : None
        data structure generated by the operator compression step, needed for the online stage, keys / values to be defined for each method
    variabilityDefinition : dict
        defines the problem variability, with variability names (typically, names of parameters) as keys
    """

    def __init__(self):

        self.problemDatas = {}
        self.reducedOrderBases = {}
        self.snapshotCorrelationOperators = {}
        self.variabilityDefinition = {}
        self.operatorCompressionData = None


    def AddReducedOrderBasis(self, solutionName, reducedOrderBasis):
        """
        Adds a reducedOrderBasis corresponding to solution solutionName

        Parameters
        ----------
        solutionName : str
            name of the solution for which reducedOrderBasis is a reduced order basis
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """
        assert isinstance(solutionName, str), "solutionName must be of type string"
        assert (
            isinstance(reducedOrderBasis, np.ndarray)
            and len(reducedOrderBasis.shape) == 2
        ), "reducedOrderBasis must be a 2D np.ndarray"

        self.reducedOrderBases[solutionName] = reducedOrderBasis

    def GetReducedOrderBasis(self, solutionName):
        """
        Get a precomputed reducedOrderBases for solution solutionName

        Parameters
        ----------
        solutionName : str
            name of the solution for which the reducedOrderBases is retrieved

        Returns
        -------
        np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """
        assert isinstance(solutionName, str), "name must be of type string"
        if solutionName not in self.reducedOrderBases:
            raise RuntimeError(
                "You must compute a reducedOrderBasis for solution named "
                + solutionName
                + " before trying to retrieve it"
            )  # pragma: no cover

        return self.reducedOrderBases[solutionName]

    def GetReducedOrderBasisNumberOfModes(self, solutionName):
        """
        Get the number of modes of a precomputed reducedOrderBases for solution solutionName

        Parameters
        ----------
        solutionName : str
            name of the solution for which the reducedOrderBases is retrieved

        Returns
        -------
        int
            numberOfModes
        """
        assert isinstance(solutionName, str), "name must be of type string"
        if solutionName not in self.reducedOrderBases:
            raise RuntimeError(
                "You must compute a reducedOrderBasis for solution named "
                + solutionName
                + " before trying to retrieve it"
            )  # pragma: no cover

        return self.GetReducedOrderBasis(solutionName).shape[0]

    def defineVariabilityAxes(self, names, types, quantities=None, descriptions=None):
        """
        Sets the axes of variability: names to be served as keys
           to collect ProblemData instances and documenting properties
           
        Parameters
        ----------
        names : tuple
           names of axes, to be served as keys
        types : type
           type of the expected values for this axis
        quantities : iterable
           (optional) describes the physical quantity of the parameter. For now an iterable of tuples (full name, unit)
        descriptions : iterable
           (optional) describes the role of the axis of variability
        """
        qlist = [None]*len(names) if quantities is None else list(quantities)
        dlist = [None]*len(names) if descriptions is None else list(descriptions)
        if not all(l==len(names) for l in (len(list(types)), len(qlist), len(dlist))):
            raise IndexError("Not all arguments to defineVariabilityAxes have the same size")
        for varname, vartype, quantity, description in zip(names, types, qlist, dlist):
            self.addVariabilityAxis(varname, vartype, quantity=quantity, description=description)
  
    def addVariabilityAxis(self, varname, vartype, **kwargs):
        """
        Sets the axes of variability: names to be served as keys
           to collect ProblemData instances and documenting properties
           
        Parameters
        ----------
        varname : str
           name of the axis, to be served as keys
        vartype : type
           type of the expected values for this axis
        quantity : tuple
           (optional) describes the physical quantity of the parameter. For now a tuple (full name, unit)
        description : str
           (optional) describes the role of the axis of variability
        """
        if varname in self.variabilityDefinition:
            raise KeyError("Variability axis {} already exists in your CollectionProblemData".format(varname))
        self.variabilityDefinition[varname] = {'type': vartype}
        for opt in ('quantity', 'description'):
            if opt in kwargs and kwargs[opt] is not None:
                self.variabilityDefinition[varname][opt] = kwargs[opt]
    
    def getNumberOfVariabilityAxes(self):
        """
        Gets the number of variability axes.
        
        Returns:
        --------
        int
            number of variability axes
        """
        return len(self.variabilityDefinition)


    def _checkPointInParameterSpace(self, **kwargs):
        """
        Checks keys and values provided as parameter point.
        
        Raises:
        --------
        ValueError
            if the number of components provided is wrong
        KeyError
            if some keyword argument does not match any known axis of variability
        TypeError
            if some value has the wrong type
        """
        if len(kwargs) != self.getNumberOfVariabilityAxes():
            raise ValueError("Provided point in parameter space has {0} components, {1} expected".format(len(kwargs), self.getNumberOfVariabilityAxes()))
        for k, v in kwargs.iteritems():
            if k not in self.variabilityDefinition:
                raise KeyError("{} is not a defined axis of variability".format(k))
            if not isinstance(v, self.variabilityDefinition[k]['type']):
                raise TypeError("Provided value {0} has type {1}, expected {2}".format(v, type(v), self.variabilityDefinition[k]['type']))

    def AddProblemData(self, problemData, **kwargs):
        """
        Adds a problemData to the structure

        Parameters
        ----------
        problemData : ProblemData
            to add to the problemDatas dictionary
        kwargs :
            same type as the axes of variability, gives the point in parameter space at which to add data
        """
        # check keys are all parameters
        
        assert isinstance(
            problemData, ProblemData.ProblemData
        ), "wrong type for problemData"
        self._checkPointInParameterSpace(**kwargs)
        self.problemDatas[tuple(kwargs.values())] = problemData
        return

    def GetProblemData(self, **kwargs):
        """
        Parameters
        ----------
        kwargs :
            same type as the axes of variability, gives the point in parameter space at which to add data
        Returns
        -------
        ProblemData
            retrieved problemData
        """
        self._checkPointInParameterSpace(**kwargs)
        return self.problemDatas[tuple(kwargs.values())]


    def GetNumberOfProblemDatas(self):
        """
        Returns
        -------
        int
            the number of problemDatas
        """
        return len(self.problemDatas.keys())


    def GetParameterDimension(self):
        """
        Assert that the parameters of all problemDatas have the same parameterDimension
        and return this size

        Returns
        -------
        int
            parameterDimension of problemDatas
        """
        # TODO: keep this method or not? Seems to add confusion.
        listParameterDimension = [
            problemData.GetParameterDimension()
            for _, problemData in self.GetProblemDatas().items()
        ]
        assert listParameterDimension.count(listParameterDimension[0]) == len(
            listParameterDimension
        )
        return listParameterDimension[0]

    def GetProblemDatas(self):
        """
        Returns
        -------
        collections.OrderedDict()
            problemDatas of the collectionProblemData
        """
        return self.problemDatas

    def GetProblemSampling(self):
        """
        Returns
        -------
        list
            list of tuples containing the computed parameter points of the available problemDatas
        """
        return list(self.GetProblemDatas().keys())

    def GetGlobalNumberOfSnapshots(self, solutionName, skipFirst = False):
        """
        Iterates over problemDatas to return the complete number of snpashots for solutions of name "solutionName"

        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to compute the total number of snapshots

        Returns
        -------
        int
            number of snpashots for solutions of name "solutionName"
        """
        if skipFirst == False:
            offset = 0
        else:
            offset = -1

        number = 0
        for _, problemData in self.problemDatas.items():
            number += problemData.solutions[solutionName].GetNumberOfSnapshots() + offset
        return number

    def GetSolutionsNumberOfComponents(self, solutionName):
        """
        Asserts that the solutions of name "solutionName" in all problemDatas have same nbeOfComponents
        and return this size

        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to return the nbeOfComponents

        Returns
        -------
        int
            nbeOfComponents of solutions of name "solutionName"
        """
        nbeOfComponents = [
            problemData.solutions[solutionName].GetNbeOfComponents()
            for _, problemData in self.GetProblemDatas().items()
        ]
        assert nbeOfComponents.count(nbeOfComponents[0]) == len(nbeOfComponents)

        return nbeOfComponents[0]

    def GetSolutionsNumberOfDofs(self, solutionName):
        """
        Asserts that the solutions of name "solutionName" in all problemDatas have same nbeOfDofs
        and return this size

        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to return the nbeOfDofs

        Returns
        -------
        int
            nbeOfDofs of solutions of name "solutionName"
        """
        nbeOfDofs = [
            problemData.solutions[solutionName].GetNumberOfDofs()
            for _, problemData in self.GetProblemDatas().items()
        ]
        assert nbeOfDofs.count(nbeOfDofs[0]) == len(nbeOfDofs)

        return nbeOfDofs[0]

    def GetSolutionsNumberOfNodes(self, solutionName):
        """
        Asserts that the solutions of name "solutionName" in all problemDatas have same nbeOfNodes
        and return this size

        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to return the nbeOfNodes

        Returns
        -------
        int
            nbeOfNodes of solutions of name "solutionName"
        """
        nbeOfNodes = [
            problemData.solutions[solutionName].GetNumberOfNodes()
            for _, problemData in self.GetProblemDatas().items()
        ]
        assert nbeOfNodes.count(nbeOfNodes[0]) == len(nbeOfNodes)

        return nbeOfNodes[0]


    def SnapshotsIterator(self, solutionName, skipFirst = False):
        """
        Constructs an iterator over snapshots of solutions of name "solutionName" in all problemDatas.

        Parameters
        ----------
        solutionName : str
            name of the solutions on which we want to iterate over snapshots

        Returns
        -------
        iterator
            an iterator over snapshots of solutions of name "solutionName" in all problemDatas
        """
        this = self

        class iterator:
            def __init__(self, solutionName, skipFirst):
                self.solutionName = solutionName
                self.skipFirst = skipFirst
                self.problemDatas = this.problemDatas

            def __iter__(self):
                for problemData in self.problemDatas.values():
                    if self.skipFirst == False:
                        localIterator = problemData.solutions[self.solutionName].snapshots.values()
                    else:
                        localIterator = list(problemData.solutions[self.solutionName].snapshots.values())[1:]
                    for snapshot in localIterator:
                        yield snapshot


        res = iterator(solutionName, skipFirst)
        return res

    def SetSnapshotCorrelationOperator(self, solutionName, snapshotCorrelationOperator):
        """
        Sets the snapshotCorrelationOperator for solution of name solutionName

        Parameters
        ----------
        solutionName : str
        snapshotCorrelationOperator : scipy.sparse.csr
        """
        self.snapshotCorrelationOperators[solutionName] = snapshotCorrelationOperator

    def GetSnapshotCorrelationOperator(self, solutionName):
        """
        Get the snapshotCorrelationOperator for solution of name solutionName. If the corresponding snapshotCorrelationOperator has not been computed, the function returns the identity matrix of correct size.

        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to return the l2ScalarProducMatrix

        Returns
        -------
        scipy.sparse.csr
            l2ScalarProducMatrix of solutions of name "solutionName"
        """
        if solutionName in self.snapshotCorrelationOperators:
            return self.snapshotCorrelationOperators[solutionName]
        else:
            print("snapshotCorrelationOperator not set, returning an identify matrix")
            return sparse.eye(self.GetSolutionsNumberOfDofs(solutionName))


    def SetOperatorCompressionData(self, operatorCompressionData):
        """
        Sets the OperatorCompressionData

        Parameters
        ----------
        operatorCompressionData : custom data structure
        """
        self.operatorCompressionData = operatorCompressionData


    def GetOperatorCompressionData(self):
        """
        Get the OperatorCompressionData

        Returns
        -------
        operatorCompressionData
            custom data structure
        """
        return self.operatorCompressionData


    def CompressSolutions(self, solutionName):
        """
        Compress solutions of name "solutionName" from all ProblemDatas in collectionProblemData, and update to corresponding solution.compressedSnapshots.

        Parameters
        ----------
        solutionName : str
            name of the solutions to compress
        """
        assert isinstance(solutionName, str)

        snapshotCorrelationOperator = self.GetSnapshotCorrelationOperator(solutionName)
        reducedOrderBasis = self.GetReducedOrderBasis(solutionName)

        for _, problemData in self.GetProblemDatas().items():
            problemData.CompressSolution(solutionName, snapshotCorrelationOperator, reducedOrderBasis)



    def SaveState(self, fileName):
        """
        Saves the data structure on disk

        Parameters
        ----------
        fileName : str
            name of the file to write on disk
        """
        import pickle

        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
            outputName = fileName + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + ".pkl"
        else:
            outputName = fileName + ".pkl"

        output = open(outputName, "wb")
        pickle.dump(self, output)
        output.close()


    def __str__(self):
        res = "CollectionProblemData\n"
        res += "number of problemDatas: " + str(self.GetNumberOfProblemDatas()) + "\n"
        res += "problemDatas: " + str(self.GetProblemSampling())
        return res


def LoadState(fileName):
    """
    Read the data structure from disk

    Parameters
    ----------
    fileName : str
        name of the file on disk
    """

    if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
        inputName = fileName + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + ".pkl"
    else:
        inputName = fileName + ".pkl"

    return pickle.load(open(inputName, "rb"))



