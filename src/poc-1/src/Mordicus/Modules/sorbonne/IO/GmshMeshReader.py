# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from mpi4py import MPI
from pathlib import Path
import os
import meshio



def ReadMesh(meshFileName):
    """
    Functional API
    
    Reads the mesh defined the Gmsh mesh file "meshFileName" (.msh)
            
    Parameters
    ----------
    meshFileName : str
        Gmsh mesh file 
                    
    Returns
    -------
    BasicToolsUnstructuredMesh
        mesh of the HF computation
    """
    reader = GmshMeshReader(meshFileName=meshFileName)
    return reader.ReadMesh()


class GmshMeshReader(MeshReaderBase):
    """
    Class containing a reader for Z-set mesh file

    Attributes
    ----------
    meshFileName : str
        name of the GMSH mesh file (.msh)
    """

    def __init__(self, meshFileName):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        super(GmshMeshReader, self).__init__()

        assert isinstance(meshFileName, str)
            

        folder = str(Path(meshFileName).parents[0])
        suffix = str(Path(meshFileName).suffix) #.msh
        stem = str(Path(meshFileName).stem) #mesh
        
        
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
        print(suffix)
        stem = str(Path(self.meshFileName).stem)
        print(stem)
        mesh=meshio.read(str(Path(self.meshFileName)))
        meshvtu= str(Path(self.meshFileName).stem)+".vtu"
        meshio.write(meshvtu,mesh)
        #from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
        from BasicTools.IO.VtuReader import VtuReader

        #raise NotImplementedError("FileName error!")
        data=VtuReader()
        mesh=data.Read(meshvtu)
        print("ok")
        return mesh
 
