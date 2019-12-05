# -*- coding: utf-8 -*-
from MordicusCore.Containers.BaseObject import BaseObject
import numpy as np

class MeshBase(BaseObject):
    """
    Class containing a MeshBase
    """
    
    def __init__(self):
        super(MeshBase,self).__init__()
        
        
        
    def GetNodes(self):
        """
        Returns
        -------
        np.ndarray
            nodes of the mesh, of size (numberOfNodes,dimensionality)
        """
        print("WARNING: I am a MeshBase! Try instanciating a particular mesh instead. Returning an empty np.ndarray")
        return np.empty((0,0))
    
    
    def AllElementsIterator(self):
        """
        Constructs an iterator over all the elements of the mesh.
        An element is np.ndarray of size (numberOfNodes,dimensionality)
        containing the indices of the nodes included in this element
        
        Returns
        -------
        iterator
            an iterator over all the elements of the mesh
        """
        raise("Not implemented in MeshBase")  #pragma: no cover   
        


    def GetNumberOfNodes(self):
        """
        Returns
        -------
        int
            the number of nodes of the mesh
        """
        return self.GetNodes().shape[0]
    

    def GetDimensionality(self):
        """
        Returns
        -------
        int
            the dimensionality of the mesh
        """
        return self.GetNodes().shape[1]


    def __str__(self):
        res = "I am a MeshBase, try instanciating a particular mesh instead"
        return res
