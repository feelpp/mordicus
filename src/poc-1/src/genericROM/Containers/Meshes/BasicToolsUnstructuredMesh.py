 # -*- coding: utf-8 -*-

from genericROM.Containers.Meshes.MeshBase import MeshBase
import numpy as np

class BasicToolsUnstructuredMesh(MeshBase):
    """
    Class containing a wrapper for the format BasicTools.Containers.UnstructuredMesh
    
    Attributes
    ----------
    __storage : BasicTools.Containers.UnstructuredMesh
    """

    def __init__(self, mesh):
        """
        Parameters
        ----------
        mesh : BasicTools.Containers.UnstructuredMesh
            the mesh wrapped to this library
        """        
        super(BasicToolsUnstructuredMesh,self).__init__()
        from BasicTools.Containers import UnstructuredMesh as UM
        assert isinstance(mesh, UM.UnstructuredMesh)
        
        self.SetInternalStorage(mesh)



    def GetNodes(self):
        return self.GetInternalStorage().nodes
    


    def AllElementsIterator(self):
        class iterator():
            def __init__(selfII, elements):
                selfII.elements = elements

            def __iter__(selfII):
                for _,data in selfII.elements.items():
                    for i in range(data.GetNumberOfElements()):
                        yield data.connectivity[i,:]
                
        res = iterator(self.GetInternalStorage().elements)
        return res
        
        
        
    def  __str__(self):
        res = str(self.GetInternalStorage())
        return res


def CheckIntegrity():
    

    from BasicTools.Containers.UnstructuredMeshTools import CreateCube
    from genericROM.Containers.Meshes import MeshTools as MT
    
    mesh = BasicToolsUnstructuredMesh(CreateCube(dimensions=[3,4,3],spacing=[2.,2.,2.],ofTetras=True))    
    
    mesh.GetNumberOfNodes()
    mesh.GetDimensionality()
    mesh.GetNodes()
    MT.ComputeL2ScalarProducMatrix(mesh, 1)
    MT.ComputeH10ScalarProductMatrix(mesh, 1)
    for el in mesh.AllElementsIterator():
        True
    
    print(mesh)
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
