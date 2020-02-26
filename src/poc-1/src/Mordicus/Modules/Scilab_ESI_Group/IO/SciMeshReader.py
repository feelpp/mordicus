import numpy as np

from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from Mordicus.Modules.Scilab_ESI_Group.Containers.Meshes.SciMesh import SciMesh
import csv
import os

class SciMeshReader(MeshReaderBase):
    """
    Reader for Scilab meshes

    Attributes
    ----------
    mesh : :class:`openturns.Mesh`
        Mesh
    """

    def __init__(self, filepath):
        super(SciMeshReader, self).__init__()

        self.filepath = filepath

        nodes = []
        with open(os.path.join(filepath,'my2Dpoints.csv')) as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                nodes.append(row)
        nodes = np.array(nodes)
        # Import Faces
        faces = []
        with open(os.path.join(filepath,'my2Dfaces.csv')) as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                faces.append(row)
        faces = np.array(faces)

        self.mesh = {
            "nodes": nodes,
            "faces": faces
        }

    def ReadMesh(self):
        """
        Returns
        -------
        MeshBase
        """
        mesh = SciMesh(self.mesh)
        return mesh