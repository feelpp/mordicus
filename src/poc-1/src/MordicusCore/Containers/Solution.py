# -*- coding: utf-8 -*-

import numpy as np
from MordicusCore.BasicAlgorithms import TimeInterpolation as TI
from MordicusCore.Containers.CompressedFormats import CompressedFormatsBase
from MordicusCore.Containers.BaseObject import BaseObject
import collections

class Solution(BaseObject):
    """
    Class containing a solution

    Attributes
    ----------
    solutionName : str
        name of the solution field (e.g. "U", "T")
    nbeOfComponents : int
        number of components of the solution (e.g. 3 for "U" in 3D, or 1 for "T")
    numberOfNodes : int
        number of nodes for the geometrical support of the solution
    numberOfDOFs : int
        number of degrees of freedom = numberOfNodes * nbeOfComponents
    primality : bool
        True for a primal solution and False for a dual solution 
    snapshots : collections.OrderedDict()
        dictionary with time indices as keys and a np.ndarray of size (numberOfDOFs,) containing the solution data
    compressedSnapshots : CompressedFormats
        a compressed representation in one of the formats defined in Containers.CompressedFormats
    """
    
    def __init__(self, solutionName, nbeOfComponents, numberOfNodes, primality):
        """
        Parameters
        ----------
        solutionName : str
        nbeOfComponents : int
        numberOfNodes : int
        primality : np.bool
        """
        super(Solution,self).__init__()
        
        assert isinstance(solutionName, str)
        assert isinstance(nbeOfComponents, int)
        assert isinstance(numberOfNodes, int)

        self.solutionName = solutionName
        self.nbeOfComponents = nbeOfComponents
        self.numberOfNodes = numberOfNodes
        self.numberOfDOFs = nbeOfComponents*numberOfNodes
        self.primality = primality
        self.snapshots = collections.OrderedDict()
        self.compressedSnapshots = None

        
        
    def AddSnapshot(self, time, snapshot):
        """
        Adds a snapshot at time "time"
        
        Parameters
        ----------
        time : float
            time of the snapshot
        snapshot : np.ndarray
            of size (numberOfDOFs,)
        """   
        
        assert isinstance(time, (float, np.float64))
        assert (len(snapshot.shape) == 1 and snapshot.shape[0] == self.numberOfDOFs)
        
        if time in self.snapshots:
            print("Snapshot at time "+time+" already in snapshots. Replacing it anyways.") #pragma: no cover
        self.snapshots[time] = snapshot
        return 
    
    

    def GetSnapshot(self, time):
        """
        Parameters
        ----------
        time : float
            time at which the snapshot is retrieved
        
        Returns
        -------
        np.ndarray
            snapshot
        """
        return self.snapshots[time]
        
        
        
    def GetTimeSequence(self):
        """
        Returns
        -------
        list
            list containing the time indices of the solution
        """
        return list(self.snapshots.keys())
    
    
    
        
    def GetSnapshotsList(self):
        """
        Returns
        -------
        list
            list containing the snapshots of the solution
        """
        return list(self.snapshots.values())
    
        
    def GetSolutionName(self):
        """
        Returns
        -------
        str
            the name of the solution field
        """
        return self.solutionName
    
        
    def GetNbeOfComponents(self):
        """
        Returns
        -------
        int
            the number of components of the solution
        """
        return self.nbeOfComponents
    
    
        
    def GetNumberOfDofs(self):
        """
        Returns
        -------
        int
            the number of degrees of freedom of the solution
        """
        return self.numberOfDOFs  
    
    
        
    def GetPrimality(self):
        """
        Returns
        -------
        bool
            the primality of the solution
        """
        return self.primality  
    
        
    def GetCompressedSnapshots(self):
        """
        Returns
        -------
        CompressedFormats
            the compressed representation of the solution
        """
        return self.compressedSnapshots  
    
        
    def GetNumberOfSnapshots(self):
        """
        Returns
        -------
        int
            the number of snapshots (= time indices) of the solution
        """
        return len(list(self.snapshots.keys()))



    def GetSolutionAtTime(self, time):
        """
        Returns
        -------
        np.ndarray
            solution value at time, of size (numberOfDOFs), using TimeInterpolation
        """
        # assert type of time
        assert isinstance(time,(np.float64,float))
        
        return TI.TimeInterpolation(time, self.GetTimeSequence(), self.GetSnapshotsList())



    def SetCompressedSnapshots(self, compressedSnapshots):
        """
        Sets the compressed representation of the solution
        
        Parameters
        ----------
        compressedSnapshots : CompressedFormats
        """
        assert (isinstance(compressedSnapshots, CompressedFormatsBase.CompressedFormatsBase)), "compressedSnapshots must be an instance of an object inheriting from Containers.CompressedFormatsBase"
        
        self.compressedSnapshots = compressedSnapshots
        return

    
    def  __str__(self):
        res = "Solution \n"
        res += "Name           : "+self.solutionName+"\n"
        res += "Dimensionality : "+str(self.nbeOfComponents)+"\n"
        res += "times          : "+str(self.GetTimeSequence())+"\n"
        if self.compressedSnapshots == None:
            res += "Not compressed" #pragma: no cover
        else:
            res += "Compressed" #pragma: no cover
        return res
