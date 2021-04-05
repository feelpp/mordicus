"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
import medcoupling as ml
import MEDLoader as ML
from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase
from Mordicus.Modules.EDF.Containers.FieldHandlers.MEDFieldHandler import safe_clone

class MEDMesh(MeshBase):
    """
    MED Mesh. In practice a wrapper to MEDFileUMesh object.
    """

    def __init__(self, meshFileName):
        """
        Constructor
        """
        super(MEDMesh, self).__init__()
        self.meshFileName = meshFileName
        MEDCouplingUMeshInstance = ml.ReadMeshFromFile(meshFileName)
        self.SetInternalStorage(MEDCouplingUMeshInstance)

    def gaussPointsCoordinates(self, sample_field):
        """
        To avoid mistakes, this start from an existing field
         
        Returns numpy array of Gauss points coordinates for a given approximation space
        """
        
        dataArray = sample_field.getLocalizationOfDiscr()
        return dataArray.toNumPyArray()

   
    def getVolume(self, sampleField):
        """Compute volume getting Gauss points from a sample field"""
        
        # deep copy field
        f = safe_clone(sampleField)
        
        # set number of components to 1
        f.changeNbOfComponents(1)
        
        # fill and compute integral
        f.fillFromAnalytic(1, "1")
        return f.integral(0, True)       

    def getNumberOfNodes(self):
        """Number of nodes of the mesh"""
        # The method has the very same name in MEDCoupling
        medCouplingUMesh = self.GetInternalStorage()
        return medCouplingUMesh.getNumberOfNodes()
        
        