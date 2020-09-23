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
mesh= meshReader.ReadMesh()
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
collectionProblemData.defineQuantity("UH", full_name="Velocity", unit="m/s")
parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds
#### Read solutions 
for i in range(ns):
    
    test=VTKSR.VTKSolutionReader("u");
    u1_np_array =test.VTKReadToNp(dataFolder+"/snapshot",i)
    u1_np_arrayH=test.VTKReadToNp(dataFolder+"/snapshotH",i) #Snapshots grossiers
    #instancie une solution
    u1_np_array=u1_np_array.flatten()
    u1_np_arrayH=u1_np_array.flatten()
    
    solutionU=S.Solution("U",dimension,numberOfNodes,True)
    solutionUH=S.Solution("UH",dimension,numberOfNodes,True)
    ### Only one snapshot --> time 0 
    solutionU.AddSnapshot(u1_np_array,0)
    solutionUH.AddSnapshot(u1_np_arrayH,0)
    problemData = PD.ProblemData(dataFolder+str(i))
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionUH)
    collectionProblemData.AddProblemData(problemData,mu1=parameters[i])
snapshotsIterator = collectionProblemData.SnapshotsIterator("U")
snapshots = []
snapshotsHIterator = collectionProblemData.SnapshotsIterator("UH")
snapshotsH = []

numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

""" Greedy """
print("-----------------------------------")
print(" STEP1: GREEDY Offline                ")
print("-----------------------------------")

print("ComputeL2ScalarProducMatrix...")
l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
ListeNorm=[]
for s in snapshotsIterator:
    snapshots.append(s)
    norm=s@(l2ScalarProducMatrix@s)
    ListeNorm.append(np.sqrt(norm))
    print("norm",np.sqrt(norm))
print("snap",np.shape(snapshots))

for s in snapshotsHIterator:#snap grossiers
    snapshotsH.append(s)

#test=NpVTK.VTKWriter(VTKBase);

##### ALGO GREEDY

nbdeg=numberOfNodes*nbeOfComponentsPrimal;
reducedOrderBasisU=np.zeros((nev,numberOfNodes*nbeOfComponentsPrimal))
reducedOrderBasisU[0,:]=snapshots[0]/ListeNorm[0] #premiere fct dans la base
ListeIndex=[0]#premier snapshot utilise

basis=[]
basis.append(np.array(snapshots[0])/ListeNorm[0])

for n in range(1,nev):
    print("nev ",n)
    testjl=[]
    testjn=[]
    for j in range(ns):
        if not (j in ListeIndex):
            
            coef=[snapshots[j]@(l2ScalarProducMatrix@b) for b in basis]
            w=snapshots[j]-np.sum(snapshots[j]@(l2ScalarProducMatrix@b)*b for b in basis)
            norml2=np.sqrt(w@(l2ScalarProducMatrix@w))
            #print("norml2 ",norml2)
            testjnorm=norml2/ListeNorm[j]
            testjl.append(testjnorm)
            testjn.append(w)
        
        else:
            testjl.append(-1)
            testjn.append(-1)
    maximum=max(testjl)
    ind=testjl.index(max(testjl))
    ListeIndex.append(ind)
    norm=np.sqrt(testjn[ind]@(l2ScalarProducMatrix@testjn[ind]))
    basis.append(testjn[ind]/norm)
    reducedOrderBasisU[n,:]=(testjn[ind]/norm)
    
collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)

#print(np.shape(reducedOrderBasisU[0,:]))
#for i in range(nev):
#    namefile="PODbase"+str(i)+".vtu"
#    test.numpyToVTKPODWrite("U", reducedOrderBasisU[i,:],namefile)
collectionProblemData.CompressSolutions("U")

#base orthonorme?

for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        print(i,j," ",norm)

# Rectification
alpha=np.zeros((ns,nev))
beta=np.zeros((ns,nev))
for i in range(ns):
    for j in range(nev):
        alpha[i,j]=snapshots[i]@(l2ScalarProducMatrix@reducedOrderBasisU[j,:])
        beta[i,j]=snapshotsH[i]@(l2ScalarProducMatrix@reducedOrderBasisU[j,:])

R=np.linalg.inv(beta.transpose()@beta+1e-10*np.eye(nev))@beta.transpose()@alpha
print(" shape R ",np.shape(R))

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

collectionProblemData.SaveState("mordicusState")

