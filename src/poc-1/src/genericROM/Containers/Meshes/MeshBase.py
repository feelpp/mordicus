# -*- coding: utf-8 -*-
from genericROM.Containers.BaseObject import BaseObject

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
        raise("Not implemented in MeshBase")  #pragma: no cover   
    
    
    
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
        from genericROM.Containers import Meshes
        allMeshes = [l for l in Meshes.__all__ if "Base" not in str(l)]
        res = "I am a MeshBase, try instanciating a particular mesh among "+str(allMeshes)+" instead"
        return res
                

def CheckIntegrity():
    # GetNumberOfNodes and GetDimensionality not tested here
    meshBase = MeshBase()
    print(meshBase)
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
