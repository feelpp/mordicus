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
from Mordicus.Modules.sorbonne.IO import FFSolutionReader as FFSR
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
from Mordicus.Core.IO import StateIO as SIO
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array
import glob



time=0.0 
dimension=2
print("NIRB online...")
## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'StationaryNSData')

FieldName="u"

print("-----------------------------------")
print(" STEP2: start Online nirb          ")
print("-----------------------------------")

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################
collectionProblemData = SIO.LoadState(dataFolder+"/collectionProblemData")
#snapshotCorrelationOperator = SIO.LoadState(dataFolder+"/Matrices/snapshotCorrelationOperator")
#h1ScalarProducMatrix=SIO.LoadState(dataFolder+"/Matrices/h1ScalarProducMatrix")
nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
l2ScalarProducMatrix = collectionProblemData.GetOperatorCompressionData()
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")


## FINE MESH reader (vtu file)
FineSolutionFileName=dataFolder+"/snapshot"+str(9)+".vtu"
FineMeshFileName=FineSolutionFileName
meshReader = MR.MeshReader(FineMeshFileName,dimension)
fineMesh = meshReader.ReadMesh()
print("Fine mesh defined in " + FineMeshFileName + " has been read")

nbeOfComponentsPrimal = 2 #number of components
numberOfNodes = fineMesh.GetNumberOfNodes()

## Coarse mesh
CoarseFileName=dataFolder+"/"+"soluH_"+str(0)+".vtu"
CoarseMeshFileName=CoarseFileName
meshReader = MR.MeshReader(CoarseMeshFileName,dimension)
coarseMesh = meshReader.ReadMesh()
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")

#coarse solution
SnapshotsReader=VTKSR.VTKSolutionReader(FieldName);

#interpolation
option="basictools"

operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)


CoarseSolution =SnapshotsReader.VTKReadToNp(CoarseFileName)
CoarseSolution=operator.dot(CoarseSolution).flatten() #coarse snapshot interpolated

solutionUH=S.Solution("U",dimension,numberOfNodes,True)

### ajouter la snapshot A solutionU
solutionUH.AddSnapshot(CoarseSolution,0)#time =0
onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUH)
Newparam=-1
collectionProblemData.AddProblemData(onlineproblemData,unused=Newparam)

#l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
#l2ScalarProducMatrix=snapshotCorrelationOperator
h1ScalarProducMatrix= FT.ComputeH10ScalarProductMatrix(fineMesh, 2)
            
    ##################################################
    # ONLINE COMPRESSION
    ##################################################
print("-----------------------------------")
print(" STEP3: Snapshot compression       ")
print("-----------------------------------")        
solutionUH.CompressSnapshots(l2ScalarProducMatrix,reducedOrderBasisU)
CompressedSolutionU = solutionUH.GetCompressedSnapshots()
reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    ##################################################
    # ONLINE ERRORS
    ##################################################
print("-----------------------------------")
print(" STEP4: L2 and H1 errors           ")
print("-----------------------------------")

print("reading exact solution...")

FineSolution =SnapshotsReader.VTKReadToNp(FineSolutionFileName).flatten()

solutionU=S.Solution("U",dimension,numberOfNodes,True)
solutionU.AddSnapshot(FineSolution,0)# Only one snapshot --> time 0
problemData = PD.ProblemData(dataFolder)
problemData.AddSolution(solutionU)
collectionProblemData.AddProblemData(problemData,unused=-1)
exactSolution =solutionU.GetSnapshot(0)
compressionErrors=[]
H1compressionErrors=[]
norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))

if norml2ExactSolution != 0 and normh1ExactSolution!=0:
    t=reconstructedCompressedSolution-exactSolution
    relError=np.sqrt(t@l2ScalarProducMatrix@t)/norml2ExactSolution
    relH1Error=np.sqrt(t@h1ScalarProducMatrix@t)/normh1ExactSolution
   
else:
    relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
H1compressionErrors.append(relH1Error)
compressionErrors.append(relError)
print("H1compressionErrors =", H1compressionErrors)
print("L2compressionErrors =", compressionErrors)
