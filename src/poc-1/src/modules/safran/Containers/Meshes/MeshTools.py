# -*- coding: utf-8 -*-
from core.Containers.Meshes import MeshBase as MB
from BasicTools.FE import FETools as FT
from modules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM


def ComputeL2ScalarProducMatrix(mesh, numberOfComponents):
    """
    Computes the L2 scalar product used to compute the correlations
    between the primal solution snapshots. The numberOfComponents
    depends on the solution type: 3 for solid mechanics in 3D, or 1 for
    thermal in any dimension
    
    Optimal input mesh format is BasicToolsUnstructuredMesh.

    Parameters
    ----------
    mesh : MeshBase
            the geometric support of the solution from one of the formats defined in Containers.Meshes
    numberOfComponents : int
        the number of components of the primal variable snapshots
        
    Returns
    -------
    scipy.sparse.csr
        the sparse matrix of the L2 scalar product
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)
    
    return FT.ComputeL2ScalarProducMatrix(unstructuredMesh, numberOfComponents)
    


def ComputeH10ScalarProductMatrix(mesh, numberOfComponents):
    """
    Computes the H10 scalar product matrix.
    
    Optimal input mesh format is BasicToolsUnstructuredMesh.
    
    Parameters
    ----------
    numberOfComponents : int
        the number of components of the primal variable snapshots
        
    Returns
    -------
    scipy.sparse.csr
        the sparse matrix of the H10 scalar product
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)
    
    return FT.ComputeH10ScalarProductMatrix(unstructuredMesh, numberOfComponents)




def ConvertMeshToUnstructuredMesh(mesh):
    
    assert (isinstance(mesh, MB.MeshBase)), "mesh must be an instance of an object inheriting from Containers.Meshes.MeshBase"
    
    if isinstance(mesh, BTUM.BasicToolsUnstructuredMesh) == False:
        """from BasicTools.Containers import UnstructuredMesh as UM
        unstructuredMesh = UM.UnstructuredMesh()
        unstructuredMesh.nodes = mesh.GetNodes()
        cpt = 0
        for name,coon in mesh.AllElementsIterator():
            eledata = mesh.elements.GetElementOfType(name)
            eledata.AddElementUsingOriginalId(coon,cpt)
            cpt += 1
        unstructuredMesh.PrepareForOutput()"""
        pass #pragma: no cover  
    else:
        unstructuredMesh = mesh.GetInternalStorage()
        
    return unstructuredMesh
                
                

def CheckIntegrity():
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
