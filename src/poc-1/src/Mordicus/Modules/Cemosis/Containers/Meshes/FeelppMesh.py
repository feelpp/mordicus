from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase

class FeelppMesh(MeshBase):
    """
    Class containing a wrapper for a feelpp mesh

    Attributes
    ----------
    __storage : feelpp.mesh
    """

    def __init__(self, mesh):
        """
        Paramaters
        ----------
        mesh : feelpp.mesh
            mesh to store
        """
        super().__init__()
        import feelpp

        assert feelpp.Environment.initialized

        self.SetInternalStorage(mesh)

    def GetDimensionality(self):
        return self.GetInternalStorage().realDimension()

    def GetNumberOfNodes(self):
        return self.GetInternalStorage().numGlobalPoints()
