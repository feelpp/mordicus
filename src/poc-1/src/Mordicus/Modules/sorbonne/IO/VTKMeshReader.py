# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from mpi4py import MPI
from pathlib import Path
import os


def VTKReadMesh(meshFileName):
    """
    Functional API
    
    Reads the mesh file "meshFileName" VTK (.vtu)
            
    Parameters
    ----------
    meshFileName : str
        VTK file 
                    
    Returns
    -------
    BasicToolsUnstructuredMesh
        mesh of the HF computation
    """

    reader = VTKMeshReader(meshFileName=meshFileName)

    return reader.ReadMesh()

def ReadVTKBase(meshFileName):
    """
    Functional API
    
    Reads the file "meshFileName" VTK (.vtu)
            
    Parameters
    ----------
    meshFileName : str
        VTK mesh and fields file 
                    
    Returns
    -------
    VTK data structure (UnstructuredMesh)
        mesh and fields of the HF computation
    """
    reader = VTKMeshReader(meshFileName=meshFileName)
    return reader.ReadVTKBase()



class VTKMeshReader(MeshReaderBase):
    """
    Class containing a reader for VTK mesh and fields file

    Attributes
    ----------
    meshFileName : str
        name of the VTK mesh file (.vtu)
    """

    def __init__(self, meshFileName):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        
        super(VTKMeshReader, self).__init__()
        

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
        #print("dans readmesh")
        suffix = str(Path(self.meshFileName).suffix)
        if suffix == ".vtu":  # pragma: no cover
            from BasicTools.IO.VtuReader import VtkToMesh as Read
            from BasicTools.IO.VtuReader import LoadVtuWithVTK 

        else:  # pragma: no cover
            raise ("FileName error!")

        data = Read(LoadVtuWithVTK(self.meshFileName))
        #print(data)
        from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM

        mesh = BTUM.BasicToolsUnstructuredMesh(data)
        
        return mesh

    def ReadVTKBase(self):
        """
        Read the HF mesh
                    
        Returns
        -------
        VTK data structure with mesh
            mesh of the HF computation
        """

        suffix = str(Path(self.meshFileName).suffix)
        if suffix == ".vtu":  # pragma: no cover
            from BasicTools.IO.VtuReader import LoadVtuWithVTK 

        else:  # pragma: no cover
            raise ("FileName error!")

        VTKBase = LoadVtuWithVTK(self.meshFileName)

        return VTKBase
