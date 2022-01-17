# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from mpi4py import MPI
from pathlib import Path
import os

def ReadMesh(meshFileName):
    """
    Functional API

    Reads the mesh defined the Z-set mesh file "meshFileName" (.geof or .geo)

    Parameters
    ----------
    meshFileName : str
        Z-set mesh file

    Returns
    -------
    BasicToolsUnstructuredMesh
        mesh of the high-fidelity computation
    """
    reader = ZsetMeshReader(meshFileName=meshFileName)
    return reader.ReadMesh()


class ZsetMeshReader(MeshReaderBase):
    """
    Class containing a reader for Z-set mesh file

    Attributes
    ----------
    meshFileName : str
        name of the Z-set mesh file (.geof or .geo)
    reader : GeoReader or GeofReader
        BasicTools reader of .geof or .geo files
    """

    def __init__(self, meshFileName):
        assert isinstance(meshFileName, str)

        super(ZsetMeshReader, self).__init__()

        folder = str(Path(meshFileName).parents[0])
        suffix = str(Path(meshFileName).suffix)
        stem = str(Path(meshFileName).stem)


        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
            meshFileName = folder + os.sep + stem + "-pmeshes" + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        else:
            meshFileName = meshFileName


        if suffix == ".geof":
            from BasicTools.IO import GeofReader as GR
            self.reader = GR.GeofReader()

        elif suffix == ".geo":  # pragma: no cover
            from BasicTools.IO import GeoReader as GR
            self.reader = GR.GeoReader()

        else:  # pragma: no cover
            raise NotImplementedError("meshFileName error!")

        self.reader.SetFileName(meshFileName)



    def ReadMesh(self):
        """
        Read the high fidelity mesh

        Returns
        -------
        BasicToolsUnstructuredMesh
            mesh of the HF computation
        """

        data = self.reader.Read()

        from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM

        mesh = BTUM.BasicToolsUnstructuredMesh(data)

        return mesh


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
