"""
Created on 26 févr. 2020

@author: Guilhem Ferte
"""
import medcoupling as ml
from Mordicus.Modules.EDF.IO.MEDMesh import MEDMesh
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase

class MEDMeshReader(MeshReaderBase):
    """
    Reader for mesh files. Based on MEDCoupling
    """
    def __init__(self, MEDFileName):
        """
        Constructor
        """
        self.meshFileName = MEDFileName
    
    def ReadMesh(self):
        """
        Reads mesh
        """
        return MEDMesh(self.meshFileName)