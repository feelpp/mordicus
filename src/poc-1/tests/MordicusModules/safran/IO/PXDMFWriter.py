# -*- coding: utf-8 -*-
import os
import numpy as np
from MordicusModules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from MordicusModules.safran.IO import PXDMFWriter as PW
from BasicTools.Containers.UnstructuredMeshTools import CreateCube
        

def test():

    
    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3,4,3],spacing=[2.,2.,2.],ofTetras=True))
    
    modes = np.ones((3,mesh.GetNumberOfNodes()))
    times = np.arange(7)
    coefficients = np.ones((7,3))
    
    from MordicusCore.Containers.CompressedFormats import ModesAndCoefficients as MAC
    compressedSnapshots = MAC.ModesAndCoefficients("U", times, 1, True) 
    compressedSnapshots.SetModes(modes) 
    compressedSnapshots.SetCoefficients(coefficients) 
    
    writer = PW.WritePXDMF(mesh, compressedSnapshots)
    
    os.system("rm -rf U_compressed0.bin U_compressed.pxdmf")
    
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
 
