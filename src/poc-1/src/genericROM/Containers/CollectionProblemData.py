# -*- coding: utf-8 -*-

import numpy as np
from scipy import sparse
from genericROM.Containers import ProblemData
from genericROM.Containers import Solution
from genericROM.Containers.BaseObject import BaseObject

class CollectionProblemData(BaseObject):
    """
    Class containing a set of collection of problemData
    
    Attributes
    ----------
    problemDatas : dict
        dictionary with problem tags (str) as keys and problemDatas (ProblemData) as values
    reducedOrderBases : dict
        dictionary with solutionNames (str) as keys and solutions (Solution) as values
    l2ScalarProducMatrix : dict
        dictionary with solutionNames (str) as keys and matrices (scipy.sparse.csr) as values
    """
    
    def __init__(self):
        super(CollectionProblemData,self).__init__()
        
        self.problemDatas           = {}
        self.reducedOrderBases      = {}
        self.l2ScalarProducMatrices = {}
        
        
        
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
        assert (isinstance(reducedOrderBasis, np.ndarray) and len(reducedOrderBasis.shape) == 2), "reducedOrderBasis must be a 2D np.ndarray"
        
        #assert that all solutions have same size and that the secnd dimension of reducedOrderBasis has this dimension
        listNumberOfDofs = [problemData1.solutions[solutionName].numberOfDOFs for _, problemData1 in self.problemDatas.items()]
        assert listNumberOfDofs.count(listNumberOfDofs[0]) == len(listNumberOfDofs)        
        assert reducedOrderBasis.shape[1] == listNumberOfDofs[0], "inconsistence dimension between reducedOrderBasis and solutions from problemDatas"
        
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
            raise("You must compute a reducedOrderBasis for solution named "+solutionName+" before trying to retrieve it") #pragma: no cover

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
            raise("You must compute a reducedOrderBasis for solution named "+solutionName+" before trying to retrieve it") #pragma: no cover

        return self.GetReducedOrderBasis(solutionName).shape[0]
        

        
    def AddProblemData(self, tag, problemData):
        """
        Adds a problemData of tag "tag"
        
        Parameters
        ----------
        tag : str
            tag given to the problemData
        problemData : ProblemData
            to add to the problemDatas dictionary
        """  
        assert isinstance(problemData, ProblemData.ProblemData), "wrong type for problemData"
        if tag in self.problemDatas:
            print("ProblemData "+tag+" already in CollectionProblemData. Replacing it anyways.") #pragma: no cover
        
        self.problemDatas[tag] = problemData
        return
    

        
        
    def GetProblemData(self, tag):
        """
        Parameters
        ----------
        tag : str
            tag of the problemData to retrieve
            
        Returns
        -------
        ProblemData
            retrieved problemData
        """
        assert isinstance(tag, str), "name must be of type string"
        if tag not in self.problemDatas:
            raise("You must add a problemData with tag "+tag+" before trying to retrieve it") #pragma: no cover

        return self.problemDatas[tag]
    
    
    
    def GetNumberOfProblemDatas(self):
        """
        Returns
        -------
        int
            the number of problemDatas
        """
        return len(self.problemDatas.keys())
    
    
    
    def GetSolutionsNumberOfDofs(self, solutionName):
        """
        Assert that the solutions of all problemDatas have the same numberOfDOFs
        and return this size
        
        Returns
        -------
        int
            numberOfDOFs of solutions solutionName
        """
        listNumberOfDofs = [problemData.solutions[solutionName].GetNumberOfDofs() for _, problemData in self.GetProblemDatas().items()]
        assert listNumberOfDofs.count(listNumberOfDofs[0]) == len(listNumberOfDofs)        
        return listNumberOfDofs[0]
    
    
    
    def GetParameterDimension(self):
        """
        Assert that the parameters of all problemDatas have the same parameterDimension
        and return this size
        
        Returns
        -------
        int
            parameterDimension of problemDatas
        """
        listParameterDimension = [problemData.GetParameterDimension() for _, problemData in self.GetProblemDatas().items()]
        assert listParameterDimension.count(listParameterDimension[0]) == len(listParameterDimension)        
        return listParameterDimension[0]
    


    def GetProblemDatas(self):
        """
        Returns
        -------
        collections.OrderedDict()
            problemDatas of the collectionProblemData
        """
        return self.problemDatas
    


    def GetProblemDatasTags(self):
        """
        Returns
        -------
        list
            list containing the tags of the available problemDatas
        """
        return list(self.GetProblemDatas().keys())



    def GetGlobalNumberOfSnapshots(self, solutionName):
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
        number = 0
        for _, problemData in self.problemDatas.items():
            number += problemData.solutions[solutionName].GetNumberOfSnapshots()
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
        nbeOfComponents = [problemData.solutions[solutionName].GetNbeOfComponents() for _, problemData in self.GetProblemDatas().items()]
        assert nbeOfComponents.count(nbeOfComponents[0]) == len(nbeOfComponents)    
        
        return nbeOfComponents[0]    
        
        
        
    def SnapshotsIterator(self, solutionName):
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
        class iterator():
            def __init__(selfII, solutionName):
                selfII.solutionName = solutionName
                selfII.problemDatas = self.problemDatas
                
            def __iter__(selfII):
                for _, problemData in selfII.problemDatas.items():
                    for _, snapshot in problemData.solutions[selfII.solutionName].snapshots.items():
                        yield snapshot
                
        res = iterator(solutionName)
        return res        
        

    
        
    def SetL2ScalarProducMatrix(self, solutionName, l2ScalarProducMatrix):
        """
        Sets the l2ScalarProducMatrix for solution of name solutionName
        
        Parameters
        ----------
        solutionName : str
        l2ScalarProducMatrix : scipy.sparse.csr
        """
        self.l2ScalarProducMatrices[solutionName] = l2ScalarProducMatrix

        
        
    def GetL2ScalarProducMatrix(self, solutionName):
        """
        Get the l2ScalarProducMatrix for solution of name solutionName. If the corresponding l2ScalarProducMatrix has not been computed, the function returns the identity matrix of correct size.
        
        Parameters
        ----------
        solutionName : str
            name of the solutions for which we want to return the l2ScalarProducMatrix
            
        Returns
        -------
        scipy.sparse.csr
            l2ScalarProducMatrix of solutions of name "solutionName"
        """
        if solutionName in self.l2ScalarProducMatrices:
            return self.l2ScalarProducMatrices[solutionName]
        else:
            print("l2ScalarProducMatrix not set, returning an identify matrix")
            numberOfDOFs = self.GetSolutionsNumberOfDofs(solutionName)
            return sparse.eye(numberOfDOFs)


    
    def  __str__(self):
        res = "CollectionProblemData\n"
        res += "number of problemDatas: "+str(self.GetNumberOfProblemDatas())+"\n"
        res += "problemDatas: "+str(list(self.problemDatas.keys()))
        return res



def CheckIntegrity():

    solution = Solution.Solution("U", 2, 10, True)
    snapshot = np.ones(20)
    snapshot2 = np.ones(20)
    solution.AddSnapshot(0., snapshot)
    solution.AddSnapshot(1., snapshot2)
    
    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)

    reducedOrderBases = np.ones((2, 20))

    collectionProblemData = CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)
    collectionProblemData.GetProblemData("computation1")
    collectionProblemData.GetProblemDatas()
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBases)
    collectionProblemData.GetReducedOrderBasis("U")
    collectionProblemData.GetNumberOfProblemDatas()
    collectionProblemData.GetSolutionsNumberOfDofs("U")
    collectionProblemData.GetProblemDatasTags()
    collectionProblemData.GetGlobalNumberOfSnapshots("U")
    collectionProblemData.GetSolutionsNumberOfComponents("U")
    collectionProblemData.SnapshotsIterator("U")
    collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    collectionProblemData.GetL2ScalarProducMatrix("U")
    collectionProblemData.SetL2ScalarProducMatrix("U", sparse.eye(20))
    collectionProblemData.GetL2ScalarProducMatrix("U")
    
    problemData.AddParameter(np.zeros(2), 0.)
    collectionProblemData.GetParameterDimension()
    print(collectionProblemData)

    return "ok"



if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
