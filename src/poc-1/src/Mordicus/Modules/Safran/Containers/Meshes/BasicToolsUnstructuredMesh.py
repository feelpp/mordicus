# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase
import numpy as np


class BasicToolsUnstructuredMesh(MeshBase):
    """
    Class containing a wrapper for the format BasicTools.Containers.UnstructuredMesh
    
    Attributes
    ----------
    __storage : BasicTools.Containers.UnstructuredMesh
    """

    def __init__(self, mesh):
        """
        Parameters
        ----------
        mesh : BasicTools.Containers.UnstructuredMesh
            the mesh wrapped to this library
        """
        super(BasicToolsUnstructuredMesh, self).__init__()
        from BasicTools.Containers import UnstructuredMesh as UM

        assert isinstance(mesh, UM.UnstructuredMesh)

        self.SetInternalStorage(mesh)

    def GetNodes(self):
        return self.GetInternalStorage().nodes
    
    def AllElementsIterator(self):
        class iterator:
            def __init__(self, elements):
                self.elements = elements

            def __iter__(self):
                for _, data in self.elements.items():
                    for i in range(data.GetNumberOfElements()):
                        yield data.connectivity[i, :]

        res = iterator(self.GetInternalStorage().elements)
        return res

    def __str__(self):
        res = str(self.GetInternalStorage())
        return res
