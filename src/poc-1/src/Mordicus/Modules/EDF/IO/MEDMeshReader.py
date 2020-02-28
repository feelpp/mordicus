"""
Created on 26 févr. 2020

@author: Guilhem Ferte
"""
import medcoupling as ml
from Mordicus.Modules.EDF.IO.MEDMesh import MEDMesh

class MEDMeshReader(object):
    """
    Reader for mesh files. Based on MEDCoupling
    """
    def __init__(self, MEDFileName):
        """
        Constructor
        """
        self.meshFileName = MEDFileName
    
    def readMesh(self):
        """
        Reads mesh
        """
        return MEDMesh(ml.ReadUMeshFromFile(self.meshFileName))