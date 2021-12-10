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

import os.path as osp

from scipy import sparse
from Mordicus.Core.Containers import ProblemData
from mpi4py import MPI
from collections import OrderedDict

class NoAxisDuplicateDict(OrderedDict):
    """A dict imposing that ('a', 'b') is invalid key if 'a' is a existing key"""

    def __setitem__(self, key, value):
        """Set self[key] to value."""
        # make an iterable from 'key'
        if isinstance(key, (str, bytes)):
            it = [key]

        # test compatibility
        for k in self.keys():
            for ke in it:
                try:
                    itk = iter(k)
                    if any([ke == i for i in itk]):#pragma: no cover
                        raise ValueError("Parameter {0} is already handled with key {1}".format(ke, k))
                except TypeError:#pragma: no cover
                    if ke == k:
                        raise ValueError("Parameter {0} is already handled with key {1}".format(ke, k))
        return OrderedDict.__setitem__(self, key, value)

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
    variabilitySupport : dict(str or tuple: ndarray)
        defines the allowed values for parameters (definition domain) and the sampling as value
    templateDataset : SolverDataset
        dataset to solve the HF problem for a new set of parameter values, contains a input_instruction_file with keywords to replace
    reducedTemplateDataset : SolverDataset
        dataset to solve the reduced problem for a new set of parameter values, contains a input_instruction_file with keywords to replace
    specificDatasets : dict(str: SolverDataset)
        dictonary with the name of the operation as key and corresponding *SolverDataset* as value
    solutionStructures : dict(str: SolutionStructure)
        dictionary of the SolutionStructure after the name of the solution
    """

    def __init__(self):

        self.problemDatas = {}
        self.reducedOrderBases = {}

        self.solutionStructures = {}
        self.variabilityDefinition = {}
        self.variabilitySupport = NoAxisDuplicateDict()
        self.quantityDefinition = {}
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

        if tuple(kwargs.values()) in self.problemDatas.keys():
            print("Warning: problemData at key "+str(tuple(kwargs.values()))+" already existing, overwriting it anyway")

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

        nbeOfComponents = []
        for _, problemData in self.GetProblemDatas().items():
            try:
                nbeOfComponents.append(problemData.GetSolution(solutionName).GetNbeOfComponents())
            except KeyError:# pragma: no cover
                continue
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

        nbeOfDofs = []
        for _, problemData in self.GetProblemDatas().items():
            try:
                nbeOfDofs.append(problemData.GetSolution(solutionName).GetNumberOfDofs())
            except KeyError:# pragma: no cover
                continue
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
                self.problemDatas = this.problemDatas
                if skipFirst == False:
                    self.startIndex = 0
                else:
                    self.startIndex = 1

            def __iter__(self):
                for problemData in self.problemDatas.values():
                    try:
                        localIterator = problemData.GetSolution(self.solutionName).GetSnapshotsList()[self.startIndex:]
                        for snapshot in localIterator:
                            yield snapshot
                    except KeyError:# pragma: no cover
                        continue

        res = iterator(solutionName, skipFirst)
        return res


    def GetSnapshots(self, solutionName, skipFirst = False):
        """
        GetSnapshots

        Returns
        -------
        np.ndarray
            of size (nbSnapshots, numberOfDofs)
        """
        self._checkSolutionName(solutionName)
        nbSnapshots = self.GetGlobalNumberOfSnapshots(solutionName, skipFirst)
        numberOfDofs = self.GetSolutionsNumberOfDofs(solutionName)

        snapshots = np.empty((nbSnapshots, numberOfDofs))
        for i, s in enumerate(self.SnapshotsIterator(solutionName, skipFirst)):
            snapshots[i,:] = s

        return snapshots



    def GetLoadingsOfType(self, type):
        """
        GetBoundaryConditionsOfType
        """
        li = []
        for _, problemData in self.GetProblemDatas().items():
            li.extend(problemData.GetLoadingsOfType(type))
        return li



    def GetSnapshotsAtTimes(self, solutionName, timeSequence):
        """
        GetSnapshotsAtTimes
        """
        self._checkSolutionName(solutionName)
        nbTimeSteps = np.array(timeSequence).shape[0]
        nbProblemDatas = self.GetNumberOfProblemDatas()
        numberOfDofs = self.GetSolutionsNumberOfDofs(solutionName)

        snapshots = np.empty((nbTimeSteps*nbProblemDatas, numberOfDofs))
        count = 0
        for problemData in self.problemDatas.values():
            solution = problemData.GetSolution(solutionName)
            for t in timeSequence:
                snapshots[count,:] = solution.GetSnapshotAtTime(t)
                count += 1

        return snapshots



    def CompressedSnapshotsIterator(self, solutionName, skipFirst = False):
        """
        Constructs an iterator over compressedSnapshots of solutions of name "solutionName" in all problemDatas.

        Parameters
        ----------
        solutionName : str
            name of the solutions on which we want to iterate over compressedSnapshots

        Returns
        -------
        iterator
            an iterator over compressedSnapshots of solutions of name "solutionName" in all problemDatas
        """
        this = self
        self._checkSolutionName(solutionName)
        class iterator:
            def __init__(self, solutionName, skipFirst):
                self.solutionName = solutionName
                self.problemDatas = this.problemDatas
                if skipFirst == False:
                    self.startIndex = 0
                else:
                    self.startIndex = 1

            def __iter__(self):
                for problemData in self.problemDatas.values():
                    localIterator  = problemData.GetSolution(self.solutionName).GetCompressedSnapshotsList()[self.startIndex :]
                    for snapshot in localIterator:
                        yield snapshot

        res = iterator(solutionName, skipFirst)
        return res



    def GetCompressedSnapshots(self, solutionName, skipFirst = False):
        """
        GetReducedSnapshots
        """
        self._checkSolutionName(solutionName)
        nbSnapshots = self.GetGlobalNumberOfSnapshots(solutionName, skipFirst)
        numberOfModes = self.GetReducedOrderBasisNumberOfModes(solutionName)

        compressedSnapshots = np.empty((nbSnapshots, numberOfModes))

        for i, s in enumerate(self.CompressedSnapshotsIterator(solutionName, skipFirst)):
            compressedSnapshots[i,:] = s

        return compressedSnapshots



    def GetCompressedSnapshotsAtTimes(self, solutionName, timeSequence):
        """
        GetCompressedSnapshotsAtTimes
        """
        self._checkSolutionName(solutionName)
        nbTimeSteps = np.array(timeSequence).shape[0]
        nbProblemDatas = self.GetNumberOfProblemDatas()
        numberOfModes = self.GetReducedOrderBasisNumberOfModes(solutionName)

        compressedSnapshots = np.empty((nbTimeSteps*nbProblemDatas, numberOfModes))
        count = 0
        for problemData in self.problemDatas.values():
            solution = problemData.GetSolution(solutionName)
            for t in timeSequence:
                compressedSnapshots[count,:] = solution.GetCompressedSnapshotsAtTime(t)
                count += 1

        return compressedSnapshots



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
            try:
                number += problemData.GetSolution(solutionName).GetNumberOfSnapshots() + offset
            except KeyError:# pragma: no cover
                continue
        return number


    def GetSolutionTimeSteps(self, solutionName, skipFirst = False):
        """
        GetTimeSteps

        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to compute the total number of snapshots
        """
        if skipFirst == False:
            startIndex = 0
        else:
            startIndex = 1

        solutionTimeSteps = np.array([])
        for _, problemData in self.problemDatas.items():
            solutionTimeSteps = np.append(solutionTimeSteps, problemData.GetSolution(solutionName).GetTimeSequenceFromSnapshots()[startIndex:], 0)

        return solutionTimeSteps


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
        Template dataset to compute reduced solution

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
        kwargs: (parameter_name=value) name of the variability as key and value stays value.
        """
        extract = kwargs.pop("extract", None)
        primalities = kwargs.pop("primalities", None)
        solutionReaderType = kwargs.pop("solutionReaderType", None)

        dataset = self.templateDataset.instantiate(**kwargs)

        # populate information for the structure
        return dataset.run(extract=extract,
                           solutionStructures=self.solutionStructures,
                           primalities=primalities,
                           solutionReaderType=solutionReaderType)

    def solve_reduced(self, **kwargs):
        """
        New high-fidelity model evaluation

        Parameters:
        -----------
         kwargs: (parameter_name=value) name of the variability as key and value stays value.
        """
        extract = kwargs.pop("extract", None)
        primalities = kwargs.pop("primalities", None)
        solutionReaderType = kwargs.pop("solutionReaderType", None)

        kwargs["reduced"] = True
        dataset = self.reducedTemplateDataset.instantiate(**kwargs)

        # populate information for the structure
        return (dataset.run(extract=extract,
                           solutionStructures=self.solutionStructures,
                           primalities=primalities,
                           solutionReaderType=solutionReaderType),
                osp.join(dataset.input_data["input_root_folder"], dataset.input_data["input_result_path"])
                            )

    def computeAPosterioriError(self, **kwargs):
        """
        Computes the residual of equilibrium. Returns a field
        """
        dataset = self.specificDatasets["computeAPosterioriError"]
        return dataset.run(**kwargs)

    def GetSolutionStructure(self, solutionName):
        """
        Parameters
        ----------
        solutionName : str
           identifier of the physical quantity, e.g. "U", "sigma"

        Returns
        -------
        SolutionStructureBase
            solution structure for the demanded solution
        """
        return self.solutionStructures[solutionName]

    def SetSolutionStructure(self, solutionName, solutionStructure):
        """
        Parameters
        ----------
        solutionName : str
           identifier of the physical quantity, e.g. "U", "sigma"
        solutionStructure : SolutionStructureBase
            solution structure for the demanded solution
        """
        self.solutionStructures[solutionName] = solutionStructure

    def defineVariabilitySupport(self, parameters, ndarrays):
        """
        Parameters
        ----------
        parameters : iterable
            iterable over the identifiers (str or tuple(str)) of parameters
        ndarrays : iterable
            iterable over the discrete support for each identifier

        Note:
            Parameters may have a tuple of parameters as a component, when the discrete
            support along these two or more parameters is not cartesian.

            Then, the corresponding ndarray has shape (numberOfPoints, numerOfParametersInTuple)

            The whole discrete support is generated as a cartesian product of discrete supports.
        """
        if len(parameters) != len(ndarrays):#pragma: no cover
            raise ValueError("Arguments 'parameters' and 'ndarrays' of defineVariabilitySupport should be of the same length.")

        for k, v in zip(parameters, ndarrays):
            self.variabilitySupport[k] = v

    def generateVariabilitySupport(self):
        """
        Realizes the catersian product to generate full grid for variability support

        Returns
        -------
        ndarray
            ndarray of shape(totalNumberOfPoints, numberOfParameters) with the coordinates of points

        Note
        ----
            on the last axis, parameters values are those of the parameters
            in the order they were declared in defineVariabilitySupport
        """
        ndarrays = self.variabilitySupport.values()
        meshgrid = np.meshgrid(*ndarrays, indexing='ij')
        return np.column_stack(tuple(m.flatten() for m in meshgrid))

    def __str__(self):
        res = "CollectionProblemData\n"
        res += "number of problemDatas: " + str(self.GetNumberOfProblemDatas()) + "\n"
        res += "problemDatas: " + str(self.GetProblemSampling())
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)





