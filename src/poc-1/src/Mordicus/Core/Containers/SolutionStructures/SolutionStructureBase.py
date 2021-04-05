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
    def __init__(self, mesh):
        self.__storage = None
        if not isinstance(mesh, MeshBase):
            raise ValueError("Attribute mesh of SolutionStructureBase should be an instance of MeshBase")
        self.mesh = mesh
        

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