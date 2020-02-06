# -*- coding: utf-8 -*-
import numpy as np
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
        mesh of the HF computation
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
    """

    def __init__(self, meshFileName):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        super(ZsetMeshReader, self).__init__()

        assert isinstance(meshFileName, str)
            

        folder = str(Path(meshFileName).parents[0])
        suffix = str(Path(meshFileName).suffix)
        stem = str(Path(meshFileName).stem)
        
        
        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover 
            self.meshFileName = folder + os.sep + stem + "-pmeshes" + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        else:
            self.meshFileName = meshFileName


    def ReadMesh(self):
        """
        Read the HF mesh
                    
        Returns
        -------
        BasicToolsUnstructuredMesh
            mesh of the HF computation
        """

        suffix = str(Path(self.meshFileName).suffix)
        if suffix == ".geof":
            from BasicTools.IO.GeofReader import ReadGeof as Read

        elif suffix == ".geo":  # pragma: no cover
            from BasicTools.IO.GeoReader import ReadGeo as Read

        else:  # pragma: no cover
            raise NotImplementedError("FileName error!")
                
        data = Read(self.meshFileName)
        

        from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM

        mesh = BTUM.BasicToolsUnstructuredMesh(data)

        return mesh
