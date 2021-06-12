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
import glob
import numpy as np
from pathlib import Path
import array


"""
Create data (mesh1,mesh2,snapshots,uH,coarsesnapshots) for Sorbonne usecase
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
#initproblem(dataFolder) #initialization of the data
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
FieldName="u"

###  convert mesh to GMSH if FF++ format and read it with Basictools
FineMeshFileName = dataFolder + "/mesh1.msh" #finemesh
CoarseMeshFileName =dataFolder + "/mesh2.msh" #coarsemesh

# FF++ snapshots filename
FFFineSolutionsFile=dataFolder+"/snapshots.txt"
FFCoarseSolutionsFile=dataFolder+"/coarsesnapshots.txt"

#print("Fine mesh: ",FineMeshFileName)
FineMeshReader=MR.MeshReader(FineMeshFileName,dimension)
FineMesh= FineMeshReader.ReadMesh()

#print("Coarse mesh: ",CoarseMeshFileName)
CoarseMeshReader=MR.MeshReader(CoarseMeshFileName,dimension)
CoarseMesh= CoarseMeshReader.ReadMesh()

nbeOfComponentsPrimal = 2 # number of components 
numberOfNodes = FineMesh.GetNumberOfNodes()
#print("number Of Nodes in the Fine Mesh",numberOfNodes)
        
collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('unused',int,description="unused parameter")
collectionProblemData.defineQuantity("U", full_name=FieldName, unit="m/s") #fine
collectionProblemData.defineQuantity("UH", full_name=FieldName, unit="m/s") #coarse

#convert FreeFem++ solutions to vtk (read the FieldName provided)

FFFinetoVTKconvert=FFSR.FFSolutionReader(FieldName,FineMeshFileName); 
FFFinetoVTKconvert.FFReadToNp(FFFineSolutionsFile) #create the snapshots with vtu format

FFCoarsetoVTKconvert=FFSR.FFSolutionReader(FieldName,CoarseMeshFileName);
FFCoarsetoVTKconvert.FFReadToNp(FFCoarseSolutionsFile) #create the snapshots with vtu format

#interpolation with GMSH mesh files
option="basictools" #ff, basictools
FineMeshFileNameGMSH =  str(Path(FineMeshFileName).parents[0])+"/"+str(Path(FineMeshFileName).stem)+"GMSH"+str(Path(FineMeshFileName).suffix)
print(FineMeshFileNameGMSH)
CoarseMeshFileNameGMSH =  str(Path(CoarseMeshFileName).parents[0])+"/"+str(Path(CoarseMeshFileName).stem)+"GMSH"+str(Path(CoarseMeshFileName).suffix)
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileNameGMSH,CoarseMeshFileNameGMSH,dimension,option=option)
#operator=SIO.LoadState(dataFolder+"/Matrices/operator") #ff

ns=1 #number of snapshots (number of files saved)
FineSnapshotFiles=sorted(glob.glob(dataFolder+"/snapshots_*"))
#print(FineSnapshotFiles)
print("number of snapshots in ", dataFolder, ": ",len(FineSnapshotFiles))
ns=len(FineSnapshotFiles)  #number of snapshots
parameters = range(ns)#for problemdata

#### Read solutions 
for i in range(ns):
    FineFileName=dataFolder+"/"+str(Path(FFFineSolutionsFile).stem)+"_"+str(i)+".vtu"
    CoarseFileName=dataFolder+"/"+str(Path(FFCoarseSolutionsFile).stem)+"_"+str(i)+".vtu"
    SnapshotsReader=VTKSR.VTKSolutionReader(FieldName);
    FineSnapshot =SnapshotsReader.VTKReadToNp(FineFileName).flatten() #fine snapshots
    CoarseSnapshot=SnapshotsReader.VTKReadToNp(CoarseFileName)
    CoarseSnapshot=operator.dot(CoarseSnapshot).flatten() #coarse snapshots interpolated

    solutionU=S.Solution("U",dimension,numberOfNodes,True)
    solutionUH=S.Solution("UH",dimension,numberOfNodes,True)
    ### Only one snapshot --> time 0 
    solutionU.AddSnapshot(FineSnapshot,0)
    solutionUH.AddSnapshot(CoarseSnapshot,0)
    problemData = PD.ProblemData(dataFolder+str(i))
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionUH)
    collectionProblemData.AddProblemData(problemData,unused=parameters[i])
    
snapshotsIterator = collectionProblemData.SnapshotsIterator("U")
snapshots = []
snapshotsHIterator = collectionProblemData.SnapshotsIterator("UH")
snapshotsH = []

#numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(FineMesh)

""" Greedy """
print("-----------------------------------")
print(" STEP1: GREEDY Offline                ")
print("-----------------------------------")

print("ComputeL2ScalarProductMatrix and h1ScalarProductMatrix...")
l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(FineMesh, 2)
h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(FineMesh, 2)

#ListeNormSnapshots=[]
for s in snapshotsIterator:
    snapshots.append(s)
    #norm=s@(l2ScalarProducMatrix@s)
    #ListeNormSnapshots.append(np.sqrt(norm))

for s in snapshotsHIterator:# coarse snapshots
    snapshotsH.append(s)

##### ALGO GREEDY
reducedOrderBasisU=GD.Greedy(snapshots,l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorithm
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U",snapshotCorrelationOperator=l2ScalarProducMatrix)

#verification orthonormalization
"""
for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        print(i,j," ",norm)
"""

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
collectionProblemData.SetDataCompressionData("rectification",R)
collectionProblemData.SetOperatorCompressionData(l2ScalarProducMatrix)
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
       
    else:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    compressionErrors.append(relError)
print("compressionErrors =", compressionErrors)

SIO.SaveState(dataFolder+"/collectionProblemData", collectionProblemData)
#SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)
