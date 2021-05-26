import os
import os.path as osp

import subprocess
import sys
#from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import FFSolutionReader as FFSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Modules.sorbonne.MOR import Greedy as GD
#from tkinter.constants import CURRENT
from initCase import initproblem

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

nev=1   #number of modes
if len(sys.argv)>1:
        nev=int(sys.argv[1])

time=0.0 
dimension=2
fieldName="u"
###  convert mesh to GMSH if necessary and read it with Basictools

meshFileName = dataFolder + "/mesh1.msh" #finemesh
coarsemeshFileName=dataFolder + "/mesh2.msh" #coarsemesh

print("Fine mesh: ",meshFileName)
meshReader=MR.MeshReader(meshFileName,dimension)
mesh= meshReader.ReadMesh()

nbeOfComponentsPrimal = 2 # vitesses 2D
numberOfNodes = mesh.GetNumberOfNodes()
print("nbNodes",numberOfNodes)
        
collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('unused',float,description="unused parameter")
collectionProblemData.defineQuantity("U", full_name=fieldName, unit="m/s")
collectionProblemData.defineQuantity("UH", full_name=fieldName, unit="m/s")

#convert FF++ solutions to vtu
test=FFSR.FFSolutionReader(fieldName,meshFileName);
test.FFReadToNp(dataFolder+"/snapshots.txt") #create folder + snapshots at vtu format

coarsetest=FFSR.FFSolutionReader(fieldName,coarsemeshFileName);
coarsetest.FFReadToNp(dataFolder+"/coarsesnapshots.txt") #create folder + snapshots at vtu format

ns=1 #number of snapshots
snapshotFiles=sorted(os.listdir(dataFolder+"/VTUSnapshots"))
coarseSnapshotFiles=sorted(os.listdir(coarseDataFolder))
print("number of snapshots in ", "VTUSnapshots", ": ",len(snapshotFiles))
ns=len(snapshotFiles)  #number of snapshots
parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds

#### Read solutions 
for i in range(ns):
    filename=dataFolder+"/VTUSnapshots/snapshot_"+str(i)+".vtu"
    test=VTKSR.VTKSolutionReader(fieldName);
    fineSnapshot =test.VTKReadToNp(filename).flatten()
    coarseSnapshot=test.VTKReadToNp(dataFolder+"/snapshotH"+str(i)+".vtu").flatten() #Snapshots grossiers
    #instancie une solution
    solutionU=S.Solution("U",dimension,numberOfNodes,True)
    solutionUH=S.Solution("UH",dimension,numberOfNodes,True)
    ### Only one snapshot --> time 0 
    solutionU.AddSnapshot(fineSnapshot,0)
    solutionUH.AddSnapshot(coarseSnapshot,0)
    problemData = PD.ProblemData(dataFolder+str(i))
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionUH)
    collectionProblemData.AddProblemData(problemData,unused=parameters[i])
    
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
h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(mesh, 2)

ListeNorm=[]
for s in snapshotsIterator:
    snapshots.append(s)
    norm=s@(l2ScalarProducMatrix@s)
    ListeNorm.append(np.sqrt(norm))

for s in snapshotsHIterator:#snap grossiers
    snapshotsH.append(s)

#test=NpVTK.VTKWriter(VTKBase);

##### ALGO GREEDY
reducedOrderBasisU=GD.Greedy(snapshots,l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorithm
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U",snapshotCorrelationOperator=l2ScalarProducMatrix)

#verification orthonormalization
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
 
lambd=1e-10
R=np.linalg.inv(beta.transpose()@beta+lambd*np.eye(nev))@beta.transpose()@alpha
#print(" shape R ",np.shape(R))
collectionProblemData.SetDataCompressionData("Rectification",R)

### Offline Errors
compressionErrors=[]

for _, problemData in collectionProblemData.GetProblemDatas().items():
    solutionU=problemData.GetSolution("U")
    CompressedSolutionU=solutionU.GetCompressedSnapshots()
    exactSolution = problemData.solutions["U"].GetSnapshot(0)
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    norml2ExactSolution=exactSolution@(l2ScalarProducMatrix@exactSolution)
        
    if norml2ExactSolution != 0:
        t=reconstructedCompressedSolution-exactSolution
       
        relError=t@(l2ScalarProducMatrix@t)/norml2ExactSolution
        #        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
    else:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    compressionErrors.append(relError)
print("compressionErrors =", compressionErrors)

SIO.SaveState("collectionProblemData", collectionProblemData)
SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)
