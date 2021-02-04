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
    MED Mesh
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


#     def gaussPointsCoordinates(self, element_group, approx_space):
#         """
#         To avoid mistakes, this start from an existing field
#         
#         Returns numpy array of Gauss points coordinates for a given approximation space
#         """
#         # Create a mesh restricted to the group
#         restrMesh = ml.ReadUMeshFromGroups(self.meshFileName, self.meshName, 0, [element_group])
#             
#         # Create a Gauss field on this mesh
#         f=ml.MEDCouplingFieldDouble(ml.ON_GAUSS_PT)
#         f.setMesh(restrMesh)
# 
#         # Create a Gauss point localization -> approximation space
#         refCoo, gpCoo, wgt = approx_space.coor_elem_ref["hexa20"], approx_space.coor_gauss["hexa20"], approx_space.weight_gauss["hexa20"]
# 
#         # TODO: replace element_type by 
#         f.setGaussLocalizationOnType(ML.NORM_HEXA20, refCoo, gpCoo, wgt)
#         dataArray = f.getLocalizationOfDiscr()
#         return dataArray.toNumPyArray()

#     def getVolumeFromApproxSpace(self, element_group, approx_space):
#         """Compute volume of mesh"""
#         # Create a mesh restricted to the group
#         restrMesh = ml.ReadUMeshFromGroups(self.meshFileName, self.meshName, 0, [element_group])
# 
#         # Create field
#         f=ml.MEDCouplingFieldDouble(ml.ON_GAUSS_PT)
#         f.setMesh(restrMesh)
# 
#         # Create a Gauss point localization -> approximation space
#         refCoo, gpCoo, wgt = approx_space.coor_elem_ref["hexa20"], approx_space.coor_gauss["hexa20"], approx_space.weight_gauss["hexa20"]
# 
#         # TODO: replace element_type by 
#         f.setGaussLocalizationOnType(ML.NORM_HEXA20, refCoo, gpCoo, wgt)
# 
#         # from https://docs.salome-platform.org/7/dev/MEDCoupling/tutorial/medcoupling_fielddouble1_fr.html#creation-d-un-champ, analytical field
#         f.fillFromAnalytic(1, "1")
#         return f.integral(0, True)
    
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
        
        