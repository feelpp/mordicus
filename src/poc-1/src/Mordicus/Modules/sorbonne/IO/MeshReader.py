# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Modules.sorbonne.IO import VTKMeshReader as VTKMR
from mpi4py import MPI
from pathlib import Path
import os


def ReadMesh(meshFileName,dimension):
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

    reader = MeshReader(meshFileName=meshFileName,dimension=dimension)
    
    return reader.ReadMesh()

class MeshReader(MeshReaderBase):
    """
    Class containing a reader for VTK mesh and fields file

    Attributes
    ----------
    meshFileName : str
        name of the VTK mesh file (.vtu)
    """

    def __init__(self, meshFileName,dimension):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        
        super(MeshReader, self).__init__()
        assert isinstance(meshFileName, str)
            
        folder = str(Path(meshFileName).parents[0])
        suffix = str(Path(meshFileName).suffix)
        stem = str(Path(meshFileName).stem)
        
        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover 
            self.meshFileName = folder + os.sep + stem + "-pmeshes" + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        else:
            self.meshFileName = meshFileName
        self.dimension=dimension


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
            vtkmeshReader = VTKMR.VTKMeshReader(self.meshFileName)
            mesh = vtkmeshReader.ReadMesh()
            if self.dimension==2:
                mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes[:,:2] #CAS 2D
            return mesh
     
        elif suffix == ".msh":
            folder = str(Path(self.meshFileName).parents[0])
            suffix = str(Path(self.meshFileName).suffix)
            stem = str(Path(self.meshFileName).stem)

            meshFileNameGMSH =  folder+"/"+stem+"GMSH"+suffix
            GMR.CheckAndConvertMeshFFtoGMSH(self.meshFileName,meshFileNameGMSH,self.dimension)
            GMSHmeshReader = GMR.GmshMeshReader(meshFileNameGMSH) #GMSHmeshReader
            mesh= GMSHmeshReader.ReadMesh()
            if self.dimension==2:
                mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes[:,:2] #CAS 2D
            return mesh

        else:
            raise ValueError  


