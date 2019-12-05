 # -*- coding: utf-8 -*-

from BasicTools.Containers.UnstructuredMeshTools import CreateCube
from MordicusModules.safran.Containers.Meshes import MeshTools as MT
from MordicusModules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM


def test():
    
    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3,4,3],spacing=[2.,2.,2.],ofTetras=True))    
    
    mesh.GetNodes()
    MT.ComputeL2ScalarProducMatrix(mesh, 1)
    MT.ComputeH10ScalarProductMatrix(mesh, 1)
    for el in mesh.AllElementsIterator():
        True
    
    print(mesh)
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
