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
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
#from tkinter.constants import CURRENT
#from initCase import initproblem
#from initCase import basisFileToArray
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
dataFolder=osp.join(currentFolder,'3DData')


## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')


print("-----------------------------------")
print(" STEP I. 0: start init             ")
print("-----------------------------------")
#initproblem(dataFolder)
print("-----------------------------------")
print("STEP I.0 (bis): snapshots generated")
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

nev=1 #default value number of modes

if len(sys.argv)>1:
        nev=int(sys.argv[1]) 

print("number of modes: ",nev)

ns=1 #number of snapshots

for root, _, files in os.walk(dataFolder+"/FineSnapshots/"):
    print("number of snapshots in ", root, ": ",len(files))
    ns=len(files)
    print("number of snapshots: ",ns)

assert nev<=ns, " !! To many number of modes, nev must be less than ns !!"
    
time=0.0 #steady 
dimension=3 #3D


## FINE MESH reader (vtu file, can also use one fine snapshot)
#FineMeshFileName=dataFolder+"/FineMesh/fineMesh.vtu"
FineMeshFileName=dataFolder+"/FineSolution/snapshot0.vtu"
meshReader = MR.MeshReader(FineMeshFileName)
fineMesh = meshReader.ReadMesh()
fineMesh.GetInternalStorage().nodes = fineMesh.GetInternalStorage().nodes
print("Fine mesh defined in " + FineMeshFileName + " has been read")

nbeOfComponentsPrimal = dimension # 3D field
numberOfNodes = fineMesh.GetNumberOfNodes()
print("number of nodes for the fineMesh: ",numberOfNodes)
#print("dimmesh",mesh.GetDimensionality())

# COARSE MESH
#CoarseMeshFileName=dataFolder+"/CoarseMesh/coarseMesh.vtu"
CoarseMeshFileName=dataFolder+"/CoarseSolution/snapshotH0.vtu"
meshReader = MR.MeshReader(CoarseMeshFileName)
coarseMesh = meshReader.ReadMesh()
coarseMesh.GetInternalStorage().nodes = coarseMesh.GetInternalStorage().nodes
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")


## READ SNAPSHOTS

print("-----------------------------------")
print(" STEP I. 1: read snapshots         ")
print("-----------------------------------")

# interpolation
option="basictools" #ff, basictools 
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,option=option)
#operator=SIO.LoadState(dataFolder+"/Matrices/operator") 


collectionProblemData = CPD.CollectionProblemData()
#collectionProblemData.addVariabilityAxis('mu',float,description="Reynolds number")
collectionProblemData.addVariabilityAxis('mu',int,description="dummy variability")
collectionProblemData.defineQuantity("U", full_name="Velocity", unit="m/s")
collectionProblemData.defineQuantity("UH", full_name="Velocity", unit="m/s")
parameters=range(ns) 

for i in range(ns):
    
    print("Reading snapshot ", i)
    VTKSnapshotReader=VTKSR.VTKSolutionReader("Velocity");
    
    u_np_array =VTKSnapshotReader.VTKReadToNp(dataFolder+"/FineSnapshots/snapshot",i)
    uH_np_array=VTKSnapshotReader.VTKReadToNp(dataFolder+"/CoarseSnapshots/snapshotH",i) #Snapshots grossiers
    
    uHh=operator.dot(uH_np_array) #interpolation of uH on fineMesh
    
    u_np_array=u_np_array.flatten()
    uH_np_array=uHh.flatten()

    solutionU=S.Solution("U",dimension,numberOfNodes,True) #Add each snapshot in collectionProblemData
    solutionUH=S.Solution("UH",dimension,numberOfNodes,True)

    solutionU.AddSnapshot(u_np_array,0) #time=0
    solutionUH.AddSnapshot(uH_np_array,0)
    
    problemData = PD.ProblemData(dataFolder+str(i)) #label of problemData=dataFolder+str(i)
    
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionUH)
    
    collectionProblemData.AddProblemData(problemData,mu=parameters[i])
    
    

#numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(fineMesh)


"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      Greedy Offline part
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

print("-----------------------------------")
print(" STEP I. 2: Create basis functions ")
print("-----------------------------------")


print("ComputeL2ScalarProducMatrix...")
#l2ScalarProducMatrix = SIO.LoadState(dataFolder+"/Matrices/snapshotCorrelationOperator") #if already created
#h1ScalarProducMatrix = SIO.LoadState(dataFolder+"/Matrices/h1ScalarProducMatrix")

#from scipy import sparse
#l2ScalarProducMatrix=sparse.eye(numberOfNodes*3) #works with identity matrix

l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(fineMesh, 3)
h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(fineMesh, 3)

# Norm of each snapshot
snapshotUIterator = collectionProblemData.SnapshotsIterator("U")
snapshots = []

SnapshotsUNorm=[]
for s in snapshotUIterator:
    snapshots.append(s)
    #t=l2ScalarProducMatrix.dot(s)
    norm=np.sqrt(s@l2ScalarProducMatrix@s)
    SnapshotsUNorm.append(norm)

    #print("norm",norm)


##### ALGO GREEDY
nbdeg=numberOfNodes*nbeOfComponentsPrimal;
reducedOrderBasisU=np.zeros((nev,nbdeg))
print("nev ",0)
reducedOrderBasisU[0,:]=snapshots[0]/SnapshotsUNorm[0] #first mode
ListIndex=[0] #first snapshot 

basis=[]
basis.append(np.array(snapshots[0]))

for n in range(1,nev):
    print("nev ",n)
    testmax=[]
    ListProj=[]
    for j in range(ns): 
        if not (j in ListIndex):
            
            coefp=[snapshots[j]@(l2ScalarProducMatrix@b) for b in basis] #previous coefficient
            proj=snapshots[j]-sum((snapshots[j]@(l2ScalarProducMatrix@b))/(b@l2ScalarProducMatrix@b)*b for b in basis) #projection 
            
            norml2=np.sqrt(proj@(l2ScalarProducMatrix@proj))
            testjnorm=norml2/SnapshotsUNorm[j]
            testmax.append(testjnorm)
            ListProj.append(proj)
        
        else:
            testmax.append(-1e23)
            ListProj.append(-1e23)
    #maximum=max(testmax)
    ind=testmax.index(max(testmax))
    #print("index :",ind)
    ListIndex.append(ind)
    norm=np.sqrt(ListProj[ind]@(l2ScalarProducMatrix@ListProj[ind]))
    basis.append(ListProj[ind])
    reducedOrderBasisU[n,:]=(ListProj[ind]/norm) #orthonormalization

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
    
reducedOrderBasisU=np.dot(changeOfBasisMatrix,reducedOrderBasisU)

for i in range(nev):
    reducedOrderBasisNorm=np.sqrt(reducedOrderBasisU[i,:]@(l2ScalarProducMatrix@reducedOrderBasisU[i,:]))
    reducedOrderBasisU[i,:]/=reducedOrderBasisNorm
   #reducedOrderBasisU[i,:]=reducedOrderBasisU[i,:]

### Add basis to collectionProblemData
    
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U", l2ScalarProducMatrix) #Mass matrix

## Ortho verification
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
print(" STEP I.3. : Rectification Offline ")
print("-----------------------------------")
snapshotUHIterator = collectionProblemData.SnapshotsIterator("UH")
snapshotsH = []

for s in snapshotUHIterator:
    snapshotsH.append(s)
    
coef=np.zeros(nev)
alpha=np.zeros((ns,nev))
beta=np.zeros((ns,nev))

for i in range(ns):
    for j in range(nev):
        alpha[i,j]=snapshots[i]@(l2ScalarProducMatrix@reducedOrderBasisU[j,:])
        beta[i,j]=snapshotsH[i]@(l2ScalarProducMatrix@reducedOrderBasisU[j,:])

lambd=1e-10 #regularization (AT@A +lambda I_d)^-1
R=np.zeros((nev,nev))
for i in range(nev):
    R[i,:]=(np.linalg.inv(beta.transpose()@beta+lambd*np.eye(nev))@beta.transpose()@alpha[:,i])
    
#print("Rectification matrix: ",R)

collectionProblemData.SetDataCompressionData("Rectification",R)


### Offline Errors
print("-----------------------------------")
print(" STEP I. 4: Offline  errors        ")
print("-----------------------------------")

L2compressionErrors=[]
H1compressionErrors=[]

for _, problemData in collectionProblemData.GetProblemDatas().items(): #for each snapshot
    solutionU=problemData.GetSolution("U")
    CompressedSolutionU=solutionU.GetCompressedSnapshots()
    exactSolution = problemData.solutions["U"].GetSnapshot(0)
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    
    norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
    normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))
    
    if norml2ExactSolution !=0 and normh1ExactSolution != 0:
        err=reconstructedCompressedSolution-exactSolution
        relL2Error=np.sqrt(err@l2ScalarProducMatrix@err)/norml2ExactSolution
        relH1Error=np.sqrt(err@h1ScalarProducMatrix@err)/normh1ExactSolution
    
    else: #erreur absolue
        relL2Error=np.sqrt(err@l2ScalarProducMatrix@err)
        relH1Error=np.sqrt(err@h1ScalarProducMatrix@err)
        
    L2compressionErrors.append(relL2Error)
    H1compressionErrors.append(relH1Error)
    
print("compression relative errors L2 =", L2compressionErrors)
print("compression relative errors H1 =", H1compressionErrors)

print("Offline DONE... ")
print("to be continued, with the online part ... ")

#save results
SIO.SaveState(dataFolder+"/OFFLINE_RESU/collectionProblemData", collectionProblemData)
#SIO.SaveState("h1ScalarProducMatrix", h1ScalarProducMatrix)
#SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)

