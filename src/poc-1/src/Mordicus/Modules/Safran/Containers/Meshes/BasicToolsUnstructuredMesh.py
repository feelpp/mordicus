# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase


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
            mesh of the high-fidelity model
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


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
