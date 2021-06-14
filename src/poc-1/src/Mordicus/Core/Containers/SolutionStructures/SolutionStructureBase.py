# coding: utf-8

from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase

class SolutionStructureBase(object):
    """
    Class containing a SolutionStructureBase, with an internal storage hidden to all its children classes

    Attributes
    ----------
    __storage : typeToDefine
        contextualization element to interpret the vector as a field
    mesh : MeshBase
        reference mesh for the definition solution is defined 
    """
    def __init__(self, mesh, discr):
        self.__storage = None
        if not isinstance(mesh, MeshBase):
            raise ValueError("Attribute mesh of SolutionStructureBase should be an instance of MeshBase")
        self.mesh = mesh
        if discr not in ("node", "gauss", "cell"):
            raise ValueError("Attribute discr of SolutionStructureBase should be one of ('node', 'gauss', 'cell')")
        self.discr = discr
        

    def SetInternalStorage(self, __storage):
        """
        Sets the internal storage
        
        Parameters
        ----------
        __storage : typeToDefine
        """
        if self.__storage is not None:
            print(
                "Internal storage already set. Replacing it anyway."
            )  # pragma: no cover
        self.__storage = __storage

    def GetInternalStorage(self):
        """
        Returns
        -------
        typeToDefine
            internal storage
        """
        if self.__storage is None:
            raise AttributeError("Please set internal storage")  # pragma: no cover
        return self.__storage
    
    def GetNumberOfNodes(self):
        """
        Returns number of points in the support of the solution
        """
        raise NotImplementedError("Meant to be implemented in derived classes")

    def GetNumberOfComponents(self):
        """
        Returns number of components of the solution
        """
        raise NotImplementedError("Meant to be implemented in derived classes")
    