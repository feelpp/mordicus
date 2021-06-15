# -*- coding: utf-8 -*-
## NIRB script python Offline part 
## Elise Grosjean
## 01/2021

import os
import os.path as osp
import glob
import sys
from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Modules.sorbonne.IO import VTKMeshReader as VTKMR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT
from BasicTools.FE import FETools as FT2
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
from Mordicus.Modules.sorbonne.MOR import Greedy as GD

#from initCase import initproblem

import numpy as np
from pathlib import Path
import array
from Mordicus.Core.IO import StateIO as SIO
from scipy import linalg

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
dataFolder=osp.join(currentFolder,'3DData/FineSnapshots/')
coarseDataFolder=osp.join(currentFolder,'3DData/CoarseSnapshots/')

## Script Files - Initiate data
#externalFolder=osp.join(currentFolder,'External')

print("-----------------------------------")
print(" STEP I. 0: start init             ")
print("-----------------------------------")
#initproblem(dataFolder) #create the snapshots 
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

nev=1 #default value number of modes

if len(sys.argv)>1:
        nev=int(sys.argv[1]) 

print("number of modes: ",nev)

time=0.0 
dimension=3
FieldName="Velocity"

snapshotFiles=sorted(os.listdir(dataFolder))
coarseSnapshotFiles=sorted(os.listdir(coarseDataFolder))

print("number of snapshots in ", dataFolder, ": ",len(snapshotFiles))
ns=len(snapshotFiles)  #number of snapshots

assert ns>0, "no snapshots file provided"
assert nev<=ns, " !! To many number of modes, nev must be less than ns !!"
assert len(coarseSnapshotFiles)==ns, " not the same number of coarse and fine snapshots!! "



## FINE MESH reader (vtu file)
FineMeshFileName=dataFolder+snapshotFiles[0]
meshReader = MR.MeshReader(FineMeshFileName,dimension)
fineMesh = meshReader.ReadMesh()
print("Fine mesh defined in " + FineMeshFileName + " has been read")

nbeOfComponentsPrimal = 3 
numberOfNodes = fineMesh.GetNumberOfNodes()
print("number of nodes for the fineMesh: ",numberOfNodes)

## COARSE MESH
CoarseMeshFileName=coarseDataFolder+"snapshotH0.vtu"
meshReader = MR.MeshReader(CoarseMeshFileName,dimension)
coarseMesh = meshReader.ReadMesh()
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")

## interpolation
option="basictools" #ff, basictools 
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)
#operator=SIO.LoadState(dataFolder+"/Matrices/operator")


## READ SNAPSHOTS

print("-----------------------------------")
print(" STEP I. 1: read snapshots         ")
print("-----------------------------------")

collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('unused',int,description=" variability")
collectionProblemData.defineQuantity("U", full_name=FieldName, unit="m/s")
collectionProblemData.defineQuantity("UH", full_name=FieldName, unit="m/s")
parameters=range(ns) #for problemdata

cpt=0 #num snapshot

## Reading fine snapshots
for file in snapshotFiles:
    print("Reading fine snapshot ", file)
    filename=dataFolder+file
    VTKSnapshotReader=VTKSR.VTKSolutionReader(FieldName)
    Fine_snapshot_array=VTKSnapshotReader.VTKReadToNp(filename).flatten()
    solutionU=S.Solution("U",dimension,numberOfNodes,True) #Add each snapshot in collectionProblemData
    solutionU.AddSnapshot(Fine_snapshot_array,0) #time=0
    problemData = PD.ProblemData(dataFolder+str(cpt)) #name of problemData
    problemData.AddSolution(solutionU)
    collectionProblemData.AddProblemData(problemData,unused=parameters[cpt])
    cpt+=1

cpt=0
## Reading coarse snapshots

for file in coarseSnapshotFiles:
    print("Reading coarse snapshot ", file)
    filename=coarseDataFolder+file
    VTKSnapshotReader=VTKSR.VTKSolutionReader(FieldName)
    
    Coarse_snapshot_array=VTKSnapshotReader.VTKReadToNp(filename)
    Coarse_snapshot_array=operator.dot(Coarse_snapshot_array).flatten() #interpolation on fineMesh
    solutionUH=S.Solution("UH",dimension,numberOfNodes,True) #Add each snapshot in collectionProblemData
    solutionUH.AddSnapshot(Coarse_snapshot_array,0) #time=0
    labelPD=dataFolder+str(cpt)
    problemData = collectionProblemData.GetProblemData(unused=parameters[cpt]) #label of problemData=parameter[cpt]
    problemData.AddSolution(solutionUH)
    #collectionProblemData.AddProblemData(problemData,mu=parameters[cpt])
    cpt+=1
    

#numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(fineMesh)

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
snapshotUHIterator = collectionProblemData.SnapshotsIterator("UH")
snapshotsH = []
for s in snapshotUHIterator:
    snapshotsH.append(s)

    
    
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

#reducedOrderBasisU=GD.Greedy(snapshots,l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorithm
reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-6, l2ScalarProducMatrix)

### Add basis to collectionProblemData
    
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U", l2ScalarProducMatrix) #Mass matrix
nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
## Ortho basis verification
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
print(" STEP I. 3. : Rectification Offline ")
print("-----------------------------------")
# determinist process: Matrix R, allows to go from coeff (uH,phi_i) to (uh,Phi_i)
print("caution: for rectification, the snapshots must be read in the same order")
    
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

print("Offline DONE ... ")
print("to be continued, with the online part ... ")

## save results
print("Save state in ", currentFolder+"/3DData/OFFLINE_RESU/collectionProblemData")

collectionProblemData.SetOperatorCompressionData(l2ScalarProducMatrix)
SIO.SaveState(currentFolder+"/3DData/OFFLINE_RESU/collectionProblemData", collectionProblemData)
#SIO.SaveState("h1ScalarProducMatrix", h1ScalarProducMatrix)
#SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)

