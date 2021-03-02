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
from Mordicus.Core.Containers import ProblemData
from mpi4py import MPI

class NoAxisDuplicateDict(dict):
    """A dict imposing that ('a', 'b') is invalid key if 'a' is a existing key"""
    def __setitem__(self, key, value):
        """Set self[key] to value."""
        # make an iterable from 'key'
        try:
            it = iter(key)
        except TypeError:
            it = [key]

        # test compatibility
        for k in self.keys():
            for ke in it:
                try:
                    itk = iter(k)
                    if any([ke == i for i in itk]):
                        raise ValueError("Parameter {0} is already handled with key {1}".format(ke, k))                       
                except TypeError:
                    if ke == k:
                        raise ValueError("Parameter {0} is already handled with key {1}".format(ke, k))
        return dict.__setitem__(self, key, value)
class CollectionProblemData(object):
    """
    Class containing a set of collection of problemData

    Attributes
    ----------
    problemDatas : dict
        dictionary with problem tags (str) as keys and problemDatas (ProblemData) as values
    reducedOrderBases : dict
        dictionary with solutionNames (str) as keys and reducedOrderBases (np.ndarray of size (numberOfModes, numberOfDOFs)) as values
    dataCompressionData : dict
        dictionary with solutionNames (str) as keys and data structure generated by the data compression step as values
    operatorCompressionData : dict
        dictionary with solutionNames (str) as keys and data structure generated by the operator compression step as values
    variabilityDefinition : dict
        defines the problem variability, with variability names (typically, names of parameters) as keys
    variabilitySupport : dict
        defines the allowed values for parameters (definition domain) and the sampling
    specificDatasets : dict
        dictonary with the name of the operation as kay and SolverDataset as value
    """

    def __init__(self):

        self.problemDatas = {}
        self.reducedOrderBases = {}

        self.fieldInstances = {}
        self.variabilityDefinition = {}
        self.variabilitySupport = {}
        self.quantityDefinition = NoAxisDuplicateDict()
        self.templateDataset = None
        self.reducedTemplateDataset = None
        self.specificDatasets = {}

        self.dataCompressionData = {}
        self.operatorCompressionData = {}

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
        self._checkSolutionName(solutionName)
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
            return None # pragma: no cover
        else:
            return self.reducedOrderBases[solutionName]
        

    def GetReducedOrderBases(self):
        """
        Get the dictionary of precomputed reducedOrderBases

        Returns
        -------
        reducedOrderBases : dict
            dictionary with solutionNames (str) as keys and reducedOrderBases (np.ndarray of size (numberOfModes, numberOfDOFs)) as values
        """
        return self.reducedOrderBases        


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
            raise IndexError("Not all arguments to defineVariabilityAxes have the same size") # pragma: no cover
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
            raise KeyError("Variability axis {} already exists in your CollectionProblemData".format(varname))  # pragma: no cover
        self.variabilityDefinition[varname] = {'type': vartype}
        for opt in ('quantity', 'description'):
            if opt in kwargs and kwargs[opt] is not None:
                self.variabilityDefinition[varname][opt] = kwargs[opt]

    def defineQuantity(self, key, full_name="", unit=""):
        """
        Define a new quantity for results

        Parameters
        ----------
        key : str
           Key to be served in ProblemData to retrieve the result
        full_name : str
           Full name of the quantity, e.g. "velocity"
        unit : str
           Measuring unit, e.g. "meter"
        """
        if not isinstance(key, str):
            raise TypeError("Quantity identifier should be a str")  # pragma: no cover
        self.quantityDefinition[key] = (full_name, unit)

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
        -------
        ValueError
            if the number of components provided is wrong
        KeyError
            if some keyword argument does not match any known axis of variability
        TypeError
            if some value has the wrong type
        """
        if len(kwargs) != self.getNumberOfVariabilityAxes():
            raise ValueError("Provided point in parameter space has {0} components, {1} expected".format(len(kwargs), self.getNumberOfVariabilityAxes()))  # pragma: no cover
        for k, v in kwargs.items():
            if k not in self.variabilityDefinition:
                raise KeyError("{} is not a defined axis of variability".format(k))  # pragma: no cover
            if not isinstance(v, self.variabilityDefinition[k]['type']):
                raise TypeError("Provided value {0} has type {1}, expected {2}".format(v, type(v), self.variabilityDefinition[k]['type']))  # pragma: no cover

    def _checkSolutionName(self, solutionName):
        """
        Checks that solutionName has been defined as a quantity identifier before.

        Argument:
        ---------
        solutionName:
            candidate identifier

        Raises:
        -------
        ValueError:
           if not
        """
        if solutionName not in self.quantityDefinition:
            raise ValueError("Solution name {} was not defined as a quantity before".format(solutionName))  # pragma: no cover


    def SetDataCompressionData(self, key, dataCompressionData):
        """
        Adds a dataCompressionData corresponding to key

        Parameters
        ----------
        key : any type
            key for which dataCompressionData corresponds
        """
        self.dataCompressionData[key] = dataCompressionData


    def GetDataCompressionData(self, key):
        """
        Get a precomputed dataCompressionData for key

        Parameters
        ----------
        key : str
            key for which dataCompressionData corresponds

        Returns
        -------
        dataCompressionData type
        """
        if key not in self.dataCompressionData:
            return None # pragma: no cover
        else:
            return self.dataCompressionData[key]


    def SetOperatorCompressionData(self, operatorCompressionData):
        """
        Sets the operatorCompressionData

        Parameters
        ----------
        operatorCompressionData : custom data structure
        """
        self.operatorCompressionData = operatorCompressionData


    def GetOperatorCompressionData(self):
        """
        Get the operatorCompressionData

        Returns
        -------
        operatorCompressionData
            custom data structure
        """
        return self.operatorCompressionData



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
        self._checkSolutionName(solutionName)
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


    def GetSnapshots(self, solutionName, skipFirst = False):
        """
        GetSnapshots
        """
        self._checkSolutionName(solutionName)
        nbSnapshots = self.GetGlobalNumberOfSnapshots(solutionName, skipFirst)
        nbDofs = self.GetSolutionsNumberOfDofs(solutionName)

        snapshots = np.empty((nbSnapshots, nbDofs))

        for i, s in enumerate(self.SnapshotsIterator(solutionName, skipFirst)):
            snapshots[i,:] = s

        return snapshots



    def CompressSolutions(self, solutionName, snapshotCorrelationOperator = None):
        """
        Compress solutions of name "solutionName" from all ProblemDatas in collectionProblemData, and update to corresponding solution.compressedSnapshots.

        Parameters
        ----------
        solutionName : str
            name of the solutions to compress
        """
        assert isinstance(solutionName, str)



        if snapshotCorrelationOperator is None:
            snapshotCorrelationOperator = sparse.eye(self.GetSolutionsNumberOfDofs(solutionName))

        reducedOrderBasis = self.GetReducedOrderBasis(solutionName)

        for _, problemData in self.GetProblemDatas().items():
            problemData.CompressSolution(solutionName, snapshotCorrelationOperator, reducedOrderBasis)


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
        for _, problemData in self.GetProblemDatas().items():
            problemData.ConvertCompressedSnapshotReducedOrderBasis(solutionName, projectedReducedOrderBasis)


    def ComputeReducedOrderBasisProjection(self, solutionName, newReducedOrderBasis, snapshotCorrelationOperator = None):
        """
        Computes the projection of reducedOrderBasis[solutionName] on newReducedOrderBases

        Parameters
        ----------
        solutionName : str
            name of the solutions to compress
        newReducedOrderBasis : np.ndarray
            of size (newNumberOfModes, numberOfDOFs)

        Returns
        -------
        np.ndarray
            of size (newNumberOfModes, numberOfModes)
        """
        assert isinstance(solutionName, str)

        if snapshotCorrelationOperator is None:
            snapshotCorrelationOperator = sparse.eye(self.GetSolutionsNumberOfDofs(solutionName))

        reducedOrderBasis = self.GetReducedOrderBasis(solutionName)

        numberOfModes = reducedOrderBasis.shape[0]
        newNumberOfModes = newReducedOrderBasis.shape[0]

        localProjectedReducedOrderBasis = np.dot(newReducedOrderBasis, snapshotCorrelationOperator.dot(reducedOrderBasis.T))

        globalProjectedReducedOrderBasis = np.zeros((newNumberOfModes, numberOfModes))
        MPI.COMM_WORLD.Allreduce([localProjectedReducedOrderBasis, MPI.DOUBLE], [globalProjectedReducedOrderBasis, MPI.DOUBLE])

        return globalProjectedReducedOrderBasis


    def SetTemplateDataset(self, templateDataset):
        """
        Template dataset to compute high-fidelity solution
        
        Parameters:
        -----------
        templateDataset : Dataset
        """
        self.templateDataset = templateDataset
        
    def SetReducedTemplateDataset(self, reducedTemplateDataset):
        """
        Template dataset to compute high-fidelity solution
        
        Parameters:
        -----------
        templateDataset : Dataset
        """
        self.reducedTemplateDataset = reducedTemplateDataset
        
    def solve(self, **kwargs):
        """
        New high-fidelity model evaluation
        
        Parameters:
        -----------
        kwargs: (parameter_name=value) keyword arguments
        """
        dataset = self.templateDataset.instantiate(**kwargs)
        
        # populate information for the structure
        return dataset.run(sampleFieldPrimal=self.fieldInstances["U"],
                           sampleFieldDual=self.fieldInstances["sigma"] )

    def solve_reduced(self, **kwargs):
        """
        New high-fidelity model evaluation
        
        Parameters:
        -----------
        kwargs: (parameter_name=value) keyword arguments
        """
        kwargs["reduced"] = True
        dataset = self.reducedTemplateDataset.instantiate(**kwargs)
        
        # populate information for the structure
        return dataset.run(sampleFieldPrimal=self.fieldInstances["U"],
                           sampleFieldDual=self.fieldInstances["sigma"] ), dataset

    def compute_equilibrium_residual(self):
        """
        Computes the residual of equilibrium. Returns a field
        """
        dataset = self.specificDatasets["compute_equilibrium_residual"]
        return dataset.run(sampleFieldPrimal=self.fieldInstances["U"],
                           extract=("r", "Fext"), method="aster")
    
    def compute_external_loading(self):
        """
        Computes the reference field for estimating the residual
        """
        dataset = self.specificDatasets["compute_external_loading"]
        return dataset.run(sampleFieldPrimal=self.fieldInstances["U"],
                           sampleFieldDual=self.fieldInstances["sigma"])

    def GetFieldInstance(self, solutionName):
        """
        Parameters:
        ----------
        problemData : ProblemData
           problemData with field Structure
        """
        return self.fieldInstances[solutionName]
    
    def SetFieldInstance(self, solutionName, fieldInstance):
        """
        Parameters:
        ----------
        problemData : ProblemData
           problemData with field Structure
        """
        self.fieldInstances[solutionName] = fieldInstance

    def defineIndexingSupport(self, parameters, **kwargs):
        """
        Parameters
        ----------
        parameters : iterable
            iterable over the identifiers (str) of parameters
        """
        self.variabilitySupport[parameters] = {}
        for opt in ('training_set'):
            if opt in kwargs and kwargs[opt] is not None:
                self.variabilitySupport[parameters][opt] = kwargs[opt]    
        

    def __str__(self):
        res = "CollectionProblemData\n"
        res += "number of problemDatas: " + str(self.GetNumberOfProblemDatas()) + "\n"
        res += "problemDatas: " + str(self.GetProblemSampling())
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)





