# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase
import feelpp


class FeelppUnstructuredMesh(MeshBase):
    """
    Class containing a wrapper for Feel++ Mesh

    Attributes
    ----------
    __storage : feelpp.Containers.UnstructuredMesh
    """

    def __init__(self, mesh):
        """
        Parameters
        ----------
        mesh : Feel++ mesh
            the mesh wrapped to this library
        """
        super(FeelppUnstructuredMesh, self).__init__()
        self.SetInternalStorage(mesh)

    def GetNodes(self):
        return self.GetInternalStorage().nodes()

    def AllElementsIterator(self):
        return feelpp.elements(self.GetInternalStorage())

    def GetDimensionality(self):
        return self.GetInternalStorage().realDimension()

    def GetNumberOfNodes(self):
        return self.GetInternalStorage().numGlobalPoints()

    def __str__(self):
        res = str(self.GetInternalStorage())
        return res



