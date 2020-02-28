"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
import medcoupling as ml
import MEDLoader as ML
from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase

class MEDMesh(MeshBase):
    """
    MED Mesh
    """


    def __init__(self, MEDCouplingUMeshInstance):
        """
        Constructor
        """
        super(MEDMesh, self).__init__()
        self.SetInternalStorage(MEDCouplingUMeshInstance)

    def gaussPointsCoordinates(self, field, element_group=None):
        """
        To avoid mistakes, this start from an existing field
        
        Returns numpy array of Gauss points coordinates for a given approximation space
        """
        dataArray = field.getLocalizationOfDiscr()
        return dataArray.toNumPyArray()

    def getVolume(self, approx_space):
        """Compute volume of mesh"""

        medCouplingUMesh = self.GetInternalStorage()

        # Create field
        f=ml.MEDCouplingFieldDouble(ml.ON_GAUSS_PT)
        f.setMesh(medCouplingUMesh)
        
        # Create a Gauss point localization -> approximation space
        refCoo, gpCoo, wgt = approx_space.coor_elem_ref["hexa20"], approx_space.coor_gauss["hexa20"], approx_space.weight_gauss["hexa20"]
        
        # TODO: replace element_type by 
        f.setGaussLocalizationOnType(ML.NORM_HEXA20, refCoo, gpCoo, wgt)
        
        # from https://docs.salome-platform.org/7/dev/MEDCoupling/tutorial/medcoupling_fielddouble1_fr.html#creation-d-un-champ, analytical field
        f.fillFromAnalytic(1, "1")
        return f.integral(0, True)
    
    def getNumberOfNodes(self):
        """Number of nodes of the mesh"""
        # The method has the very same name in MEDCoupling
        medCouplingUMesh = self.GetInternalStorage()
        return medCouplingUMesh.getNumberOfNodes()
        
        