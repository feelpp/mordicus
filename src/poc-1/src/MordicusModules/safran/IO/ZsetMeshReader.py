# -*- coding: utf-8 -*-
import numpy as np

from MordicusCore.IO.MeshReaderBase import MeshReaderBase

    

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
    reader = ZsetMeshReader(meshFileName = meshFileName)
    return reader.ReadMesh()



class ZsetMeshReader(MeshReaderBase):
    """
    Class containing a reader for Z-set mesh file

    Attributes
    ----------
    meshFileName : str
        name of the Z-set mesh file (.geof or .geo)
    """
    
    def __init__(self, meshFileName = None):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        super(ZsetMeshReader,self).__init__()
        
        assert isinstance(meshFileName,str) or meshFileName is None
        
        self.meshFileName     = meshFileName


    def ReadMesh(self):
        """
        Read the HF mesh
                    
        Returns
        -------
        BasicToolsUnstructuredMesh
            mesh of the HF computation
        """
        if self.meshFileName[-5:] == ".geof":
            from BasicTools.IO import GeofReader as GR
            data = GR.ReadGeof(self.meshFileName)
        elif self.meshFileName[-4:] == ".geo": #pragma: no cover
            from BasicTools.IO import GeoReader as GR
            data = GR.ReadGeo(self.meshFileName)
        else: #pragma: no cover
            raise("FileName error!")
            
        from MordicusModules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
        mesh = BTUM.BasicToolsUnstructuredMesh(data)

        return mesh
