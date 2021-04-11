"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase

class MEDMesh(MeshBase):
    """
    MED Mesh. In practice a wrapper to MEDFileUMesh object.
    """

    def __init__(self, mf_mesh):
        """
        Constructor
        
        Arguments
        ---------
        mf_mesh : MEDFileUMesh from MEDLoader
        """
        super(MEDMesh, self).__init__()
        self.SetInternalStorage(mf_mesh)    

    def getNumberOfNodes(self):
        """Number of nodes of the mesh"""
        # The method has the very same name in MEDCoupling
        mf_mesh = self.GetInternalStorage()
        return mf_mesh.getNumberOfNodes()
        
        