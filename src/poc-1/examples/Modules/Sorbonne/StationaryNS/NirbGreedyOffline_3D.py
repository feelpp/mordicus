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
from BasicTools.FE import FETools as FT2
from Mordicus.Modules.CT.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
#from tkinter.constants import CURRENT
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array
from Mordicus.Core.IO import StateIO as SIO
from scipy import linalg
#from Mordicus.Modules.sorbonne.IO.FFSolutionReader import FFSolutionReader
import sys
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
#initproblem(dataFolder)
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
nev=int(sys.argv[1])#11   #nombre de modes
print(nev)
ns=22
time=0.0 
dimension=3
           
## FINE MESH
meshFileName=dataFolder+"/mesh1.vtu"
meshReader = MR.MeshReader(meshFileName)
mesh = meshReader.ReadMesh()
mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes

VTKBase = MR.ReadVTKBase(dataFolder+"/mesh1.vtu")
print("Mesh defined in " + meshFileName + " has been read")

nbeOfComponentsPrimal = 3 # vitesses 3D
numberOfNodes = mesh.GetNumberOfNodes()
#print("nbNodes",numberOfNodes)
#print("dimmesh",mesh.GetDimensionality())


## READ SNAPSHOTS
print("-----------------------------------")
print(" STEP0bis: read snapshots             ")
print("-----------------------------------")
collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('mu1',float,description="Reynolds number")
collectionProblemData.defineQuantity("U", full_name="Velocity", unit="m/s")
collectionProblemData.defineQuantity("UH", full_name="Velocity", unit="m/s")
parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds

for i in range(ns):
    
    test=VTKSR.VTKSolutionReader("Velocity");
    u1_np_array =test.VTKReadToNp(dataFolder+"/snapshot",i)
    u1_np_arrayH=test.VTKReadToNp(dataFolder+"/snapshotH",i) #Snapshots grossiers
    #instancie une solution
    u1_np_array=u1_np_array.flatten()
    #print(np.shape(u1_np_array))
    u1_np_arrayH=u1_np_arrayH.flatten()
    #print(np.shape(u1_np_arrayH))
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


print("-----------------------------------")
print(" STEP1: Greedy Offline             ")
print("-----------------------------------")

print("ComputeL2ScalarProducMatrix...")
l2ScalarProducMatrix = SIO.LoadState("snapshotCorrelationOperator")
#from scipy import sparse
#l2ScalarProducMatrix=sparse.eye(numberOfNodes*3)#.toarray()
#l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)

print("computeH1ScalarProducMatrix...")
h1ScalarProducMatrix=SIO.LoadState("h1ScalarProducMatrix")
#FT.ComputeH10ScalarProductMatrix(mesh, 3)
#SIO.SaveState("h1ScalarProducMatrix", h1ScalarProducMatrix)

ListeNorm=[]
for s in snapshotsIterator:
    snapshots.append(s)
    t=l2ScalarProducMatrix.dot(s)
    norm=np.sqrt(t.dot(s))
    ListeNorm.append(norm)
    #print("norm",norm)
#print("snap",np.shape(snapshots))

for s in snapshotsHIterator:#snap grossiers
    snapshotsH.append(s)
    t=l2ScalarProducMatrix.dot(s)
    norm=np.sqrt(t.dot(s))
    #print("norm",norm)

##### ALGO GREEDY
nbdeg=numberOfNodes*nbeOfComponentsPrimal;
reducedOrderBasisU=np.zeros((nev,numberOfNodes*nbeOfComponentsPrimal))
reducedOrderBasisU[0,:]=snapshots[0]/ListeNorm[0] #first mode
ListeIndex=[0]#first snapshot 

basis=[]
basis.append(np.array(snapshots[0]))

for n in range(1,nev):
    print("nev ",n)
    testjl=[]
    testjn=[]
    for j in range(ns): 
        if not (j in ListeIndex):
            
            coef=[snapshots[j]@(l2ScalarProducMatrix@b) for b in basis]
            w=snapshots[j]-np.sum((snapshots[j]@(l2ScalarProducMatrix@b))/(b@l2ScalarProducMatrix@b)*b for b in basis)
            
            norml2=np.sqrt(w@(l2ScalarProducMatrix@w))
            #print("norml2 ",norml2)
            testjnorm=norml2/ListeNorm[j]
            testjl.append(testjnorm)
            testjn.append(w)
        
        else:
            testjl.append(-1e23)
            testjn.append(-1e23)
    maximum=max(testjl)
    ind=testjl.index(max(testjl))
    print("index",ind)
    ListeIndex.append(ind)
    norm=np.sqrt(testjn[ind]@(l2ScalarProducMatrix@testjn[ind]))
    basis.append(testjn[ind])
    reducedOrderBasisU[n,:]=(testjn[ind]/norm)

### H1 & L2 Orthogonalization

K=np.zeros((nev,nev))
M=np.zeros((nev,nev))
for i in range(nev):
    for j in range(nev):
        K[i,j]=reducedOrderBasisU[i,:]@h1ScalarProducMatrix@reducedOrderBasisU[j,:]
        M[i,j]=reducedOrderBasisU[i,:]@l2ScalarProducMatrix@reducedOrderBasisU[j,:]
eigenValues,vr=linalg.eig(K, b=M)#eigenvalues + right eigenvectors
idx = eigenValues.argsort()[::-1]
eigenValues = eigenValues[idx]
eigenVectors = vr[:, idx]
changeOfBasisMatrix = np.zeros((nev,nev))
for j in range(nev):
    changeOfBasisMatrix[j,:]=eigenVectors[:,j]
reducedOrderBasis=np.dot(changeOfBasisMatrix,reducedOrderBasisU)

for i in range(nev):
    reducedOrderBasisNorm=np.sqrt(reducedOrderBasis[i,:]@(l2ScalarProducMatrix@reducedOrderBasis[i,:]))
    reducedOrderBasis[i,:]/=reducedOrderBasisNorm
    reducedOrderBasisU[i,:]=reducedOrderBasis[i,:]

### Add basis to collectionProblemData
    
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U", l2ScalarProducMatrix)

## Ortho verif
"""
for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        normh1=reducedOrderBasisU[i,:]@(h1ScalarProducMatrix@reducedOrderBasisU[j,:])
        print(i,j," ",norm)
        print(" normh1 ", normh1)
"""
        
### PT: Rectification
print("-----------------------------------")
print(" STEP1bis: Rectification Offline   ")
print("-----------------------------------")

coef=np.zeros(nev)
alpha=np.zeros((ns,nev))
beta=np.zeros((ns,nev))

for i in range(ns):
    for j in range(nev):
        alpha[i,j]=snapshots[i]@(l2ScalarProducMatrix@reducedOrderBasisU[j,:])
        beta[i,j]=snapshotsH[i]@(l2ScalarProducMatrix@reducedOrderBasisU[j,:])

lambd=1e-10
R=np.zeros((nev,nev))
for i in range(nev):
    R[i,:]=(np.linalg.inv(beta.transpose()@beta+lambd*np.eye(nev))@beta.transpose()@alpha[:,i])
    
#print("R",R)

collectionProblemData.SetDataCompressionData("Rectification",R)



### Offline Errors
print("-----------------------------------")
print(" STEP1bis: Offline  errors ")
print("-----------------------------------")

compressionErrors=[]
h1compressionErrors=[]

for _, problemData in collectionProblemData.GetProblemDatas().items():
    solutionU=problemData.GetSolution("U")
    CompressedSolutionU=solutionU.GetCompressedSnapshots()
    exactSolution = problemData.solutions["U"].GetSnapshot(0)
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    
    norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
    normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))
    if norml2ExactSolution !=0 and normh1ExactSolution != 0:
        t=reconstructedCompressedSolution-exactSolution
        relError=np.sqrt(t@l2ScalarProducMatrix@t)/norml2ExactSolution
        relh1Error=np.sqrt(t@h1ScalarProducMatrix@t)/normh1ExactSolution
    
    else:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    compressionErrors.append(relError)
    h1compressionErrors.append(relh1Error)
print("compressionErrors =", compressionErrors)
print("compressionErrorsh1 =", h1compressionErrors)
print("Offline termine")
SIO.SaveState("collectionProblemData", collectionProblemData)
#SIO.SaveState("h1ScalarProducMatrix", h1ScalarProducMatrix)
#SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)

