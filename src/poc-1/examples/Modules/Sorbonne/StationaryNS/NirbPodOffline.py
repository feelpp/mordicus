import os
import os.path as osp

import subprocess

from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT
from  Mordicus.Modules.CT.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
#from tkinter.constants import CURRENT
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array


#from Mordicus.Modules.sorbonne.IO.FFSolutionReader import FFSolutionReader

"""
Create data (mesh1,mesh2,snapshots,uH) for Sorbonne usecase
"""
"""
----------------------------
              generate snapshots
----------------------------
"""

## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'StationaryNSData')


## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')


print("-----------------------------------")
print(" STEP0: start init                 ")
print("-----------------------------------")
initproblem(dataFolder)
print("-----------------------------------")
print(" STEP0: snapshots generated        ")
print("-----------------------------------")

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      Definition and initialisation of the problem
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
nev=5   #nombre de modes
ns=10
time=0.0
dimension=2

###  convert mesh to GMSH if necessary and read it with Basictools

meshFileName = dataFolder + "/mesh1.msh"
print("init fine mesh: ",meshFileName)
meshFileNameGMSH = dataFolder + "/mesh1GMSH.msh"
GMR.CheckAndConvertMeshFFtoGMSH(meshFileName,meshFileNameGMSH)

meshReader = GMR.GmshMeshReader(meshFileNameGMSH)
mesh = meshReader.ReadMesh()
mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes[:,:2] #CAS 2D

### Convert mesh to VTU
"""
try:
    FNULL=open(os.devnull,'w')
    ret=subprocess.run(["meshio-convert", meshFileNameGMSH, dataFolder+"/mesh1.vtu"], stdout=FNULL, stderr=subprocess.PIPE)
    ret.check_returncode()
except subprocess.CalledProcessError:
    retstr="Error File convertion with meshio\n" + "    Returns error:\n" + str(ret.stderr)
    raise OSError(ret.returncode,retstr)

VTKBase = MR.ReadVTKBase(dataFolder+"/mesh1.vtu")
"""
print("Mesh defined in " + meshFileNameGMSH + " has been read")
nbeOfComponentsPrimal = 2 # vitesses 2D
numberOfNodes = mesh.GetNumberOfNodes()
#print("nbNodes",numberOfNodes)
#print("dimmesh",mesh.GetDimensionality())

collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('mu1',float,description="Reynolds number")
collectionProblemData.defineQuantity("U", full_name="Velocity", unit="m/s")

parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds
#### Read solutions 
for i in range(ns):

    test=VTKSR.VTKSolutionReader("u");
    u1_np_array =test.VTKReadToNp(dataFolder+"/snapshot",i)

    #instancie une solution
    u1_np_array=u1_np_array.flatten()

    solutionU=S.Solution("U",dimension,numberOfNodes,True)
 
    ### Only one snapshot --> time 0
    solutionU.AddSnapshot(u1_np_array,0)
    problemData = PD.ProblemData(dataFolder+str(i))
    problemData.AddSolution(solutionU)
    collectionProblemData.AddProblemData(problemData,mu1=parameters[i])
snapshotsIterator = collectionProblemData.SnapshotsIterator("U")
snapshots = []

numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

""" POD """
print("-----------------------------------")
print(" STEP1: POD Offline                ")
print("-----------------------------------")

print("ComputeL2ScalarProducMatrix...")
l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
"""for s in snapshotsIterator:
    snapshots.append(s)
    t=l2ScalarProducMatrix.dot(s)
    norm=t.dot(s)
    print("norm",np.sqrt(norm))
print("snap",np.shape(snapshots))"""

#test=NpVTK.VTKWriter(VTKBase);

#collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)
#snapshotCorrelationOperator=collectionProblemData.GetSnapshotCorrelationOperator("U")
reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-4, l2ScalarProducMatrix)

collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)

#print(np.shape(reducedOrderBasisU[0,:]))
#for i in range(nev):
#    namefile="PODbase"+str(i)+".vtu"
#    test.numpyToVTKPODWrite("U", reducedOrderBasisU[i,:],namefile)

#base orthonorme?

for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        print(i,j," ",norm)


### Offline Errors

compressionErrors=[]

for _, problemData in collectionProblemData.GetProblemDatas().items():
    solutionU=problemData.GetSolution("U")
    CompressedSolutionU=solutionU.GetCompressedSnapshots()
    exactSolution = problemData.solutions["U"].GetSnapshot(0)
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    t=l2ScalarProducMatrix.dot(exactSolution)
    norml2ExactSolution=t.dot(exactSolution)
        
    if norml2ExactSolution != 0:
        t=l2ScalarProducMatrix.dot(reconstructedCompressedSolution-exactSolution)
        relError=t.dot(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
        #        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
    else:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    compressionErrors.append(relError)
print("compressionErrors =", compressionErrors)

SIO.SaveState("collectionProblemData", collectionProblemData)
SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)

