import numpy as np

from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from Mordicus.Modules.Phimeca.Containers.Meshes.OTMesh import OTMesh

class OTMeshReader(MeshReaderBase):
    """
    Reader for OpenTURNS meshes

    Attributes
    ----------
    mesh : :class:`openturns.Mesh`
        Mesh
    """
    def __init__(self, ot_mesh):
        super(OTMeshReader, self).__init__()
        self.ot_mesh = ot_mesh

    def ReadMesh(self):
        """
        Returns
        -------
        MeshBase
        """
        mesh = OTMesh(self.ot_mesh)
        return mesh
