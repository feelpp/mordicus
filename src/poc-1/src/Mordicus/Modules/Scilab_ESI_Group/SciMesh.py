# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase
import numpy as np


class SciMesh(MeshBase):
    """
    Class containing a wrapper for the format openturns.Mesh

    Attributes
    ----------
    __storage : openturns.Mesh
    """

    def __init__(self, mesh):
        """
        Parameters
        ----------
        mesh : openturns.Mesh
            the mesh wrapped to this library
        """
        super(SciMesh, self).__init__()

        #assert isinstance(mesh, ot.Mesh)

        self.SetInternalStorage(mesh)

    def GetNodes(self):
        return self.GetInternalStorage().get("nodes")

    def AllElementsIterator(self):
        class iterator:
            def __init__(self, simplices):
                self.simplices = simplices

            def __iter__(self):
                for simplex in self.simplices:
                    yield np.array(simplex)

        res = iterator(self.GetInternalStorage().getSimplices())
        return res

    def __str__(self):
        res = str(self.GetInternalStorage())
        return res
