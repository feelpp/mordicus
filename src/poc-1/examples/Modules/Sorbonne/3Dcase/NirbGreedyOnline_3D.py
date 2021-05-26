import os
import os.path as osp

import subprocess

from Mordicus.Modules.sorbonne.IO import VTKMeshReader as VTKMR
from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT
from BasicTools.FE import FETools as FT2
from BasicTools.FE.Fields.FEField import FEField
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
from Mordicus.Core.IO import StateIO as SIO
#from initCase import initproblem
#from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array
import sys


print("-----------------------------------")
print(" STEP II. 0: start Online nirb     ")
print("-----------------------------------")


time=0.0 #steady
dimension=3 #3D

## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'3DData','FineSnapshots') # exact solution
basisResuFolder=osp.join(currentFolder,'3DData','OFFLINE_RESU')
coarseDataFolder=osp.join(currentFolder,'3DData','CoarseSnapshots') # exact coarse solution
## Field name
nameField="Velocity"
## Fine and coarse Solution files name
coarseName="snapshotH0.vtu"
fineName="snapshot0.vtu"

###########################
# LOAD DATA FOR ONLINE
###########################

collectionProblemData = SIO.LoadState(currentFolder+"/3DData/OFFLINE_RESU/collectionProblemData")
#h1ScalarProducMatrix=SIO.LoadState(dataFolder+"/Matrices/h1ScalarProducMatrix")
nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
l2ScalarProducMatrix = collectionProblemData.GetOperatorCompressionData()
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")
R=collectionProblemData.GetDataCompressionData("Rectification")
#print("Rectification matrix: ", R)

#### LOAD FINE MESH
FineMeshFileName=dataFolder+"/snapshot0.vtu"
meshReader = MR.MeshReader(FineMeshFileName,dimension)
fineMesh = meshReader.ReadMesh()
print("Fine mesh defined in " + FineMeshFileName + " has been read")

nbeOfComponentsPrimal = 3 # vitesses 3D
numberOfNodes = fineMesh.GetNumberOfNodes()

h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(fineMesh, 3)

#### LOAD COARSE MESH
CoarseMeshFileName=coarseDataFolder+"/snapshotH0.vtu"
meshReader = MR.MeshReader(CoarseMeshFileName,dimension)
coarseMesh = meshReader.ReadMesh()
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")


print("-------------------------------------------------")
print(" STEP II. 1: Read and interpolate Coarse Solution")
print("-------------------------------------------------")

##################################################
#### Interpolation coarse solution on fine mesh 
##################################################

## FreeFem++, basictools interpolation , python

option="basictools" #ff or basictools
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)
# operator=SIO.LoadState(dataFolder+"/Matrices/operator")


# Reading coarse solution
VTKSnapshotReader=VTKSR.VTKSolutionReader(nameField);
CoarseExactSolution =VTKSnapshotReader.VTKReadToNp(coarseDataFolder+"/"+coarseName) 
print("coarse solution in "+ coarseDataFolder + " has been read ")

# Compute the projected data using the interpolation operator
if option=="ff":
    CoarseExactSolution=CoarseExactSolution.flatten() 
    
CoarseExactSolution = operator.dot(CoarseExactSolution) #interpolation

if option=="ff":
   CoarseExactSolution=CoarseExactSolution.reshape((numberOfNodes, 3)) #if ff


# save interpolated solution
"""
VTKBase = MR.ReadVTKBase(FineMeshFileName)
SnapWrite=NpVTK.VTKWriter(VTKBase)
SnapWrite.numpyToVTKSanpWrite(CoarseExactSolution,currentFolder+"/uHh.vtu")
# read interpolated solution
#CoarseExactSolution =VTKSnapshotReader.VTKReadToNp(dataFolder+"/CoarseSolutionInterp/uHh",0)
"""

CoarseExactSolution=CoarseExactSolution.flatten()
solutionUHh=S.Solution("U",dimension,numberOfNodes,True)
solutionUHh.AddSnapshot(CoarseExactSolution,0)

onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUHh)

UnusedParam=0 #Problem Data label
collectionProblemData.AddProblemData(onlineproblemData,unused=UnusedParam)

##################################################
# ONLINE COMPRESSION
##################################################

print("--------------------------------")
print(" STEP II. 2:  Online compression")
print("--------------------------------")

solutionUHh.CompressSnapshots(l2ScalarProducMatrix,reducedOrderBasisU)
CompressedSolutionU = solutionUHh.GetCompressedSnapshots()

# Rectification

coef=np.zeros(nev)
for i in range(nev):
    coef[i]=0
    for j in range(nev):
        coef[i]+=R[i,j]*CompressedSolutionU[0][j]
        
#print("coef without rectification: ", CompressedSolutionU[0])
#print("coef with rectification ", coef)

reconstructedCompressedSolution = np.dot(coef, reducedOrderBasisU) #with rectification
#reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0

##################################################
# SAVE APPROXIMATION
##################################################

VTKBase = VTKMR.ReadVTKBase(FineMeshFileName)
SnapWrite=NpVTK.VTKWriter(VTKBase)
savedata=reconstructedCompressedSolution.reshape((numberOfNodes, 3)) #if ff
SnapWrite.numpyToVTKSanpWrite(savedata,currentFolder+"/3DData/ONLINE_RESU/NIRB_Greedy_Approximation_"+str(nev)+".vtu")


##################################################
# ONLINE ERRORS
##################################################

if fineName!="":
    print("-----------------------------------")
    print(" STEP II. 3: L2 and H1 errors      ")
    print("-----------------------------------")


    print("reading exact solution...")
    exactSolution=VTKSnapshotReader.VTKReadToNp(dataFolder+"/"+fineName).flatten()

    solutionU=S.Solution("U",dimension,numberOfNodes,True)
    solutionU.AddSnapshot(exactSolution,0) #only one snapshot->time=0

    problemData = PD.ProblemData(dataFolder)
    problemData.AddSolution(solutionU)
    collectionProblemData.AddProblemData(problemData,unused=UnusedParam)
    
    exactSolution =solutionU.GetSnapshot(0)
    solutionU.CompressSnapshots(l2ScalarProducMatrix,reducedOrderBasisU)

    #relative errors list
    L2compressionErrors=[]
    H1compressionErrors=[]

    norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
    normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))

    err=reconstructedCompressedSolution-exactSolution
    if norml2ExactSolution != 0 and normh1ExactSolution != 0:
        
        L2relError=np.sqrt(err@(l2ScalarProducMatrix@err))/norml2ExactSolution
        H1relError=np.sqrt(err@h1ScalarProducMatrix@err)/normh1ExactSolution
        """
        f = open("NIRB_Greedy_errorH1.txt", "a")
        f.write("nev ")
        f.write(str(nev))
        f.write(" : ")
        f.write(str(H1relError))
        f.write("\n")
        f.close()
        """
    else:
        print("norm exact solution = 0")
        L2relError=np.sqrt(err@(l2ScalarProducMatrix@err))
        H1relError=np.sqrt(err@h1ScalarProducMatrix@err)
    
L2compressionErrors.append(L2relError)
H1compressionErrors.append(H1relError)

print("compression relative errors L2 with nev ", str(nev), " = ", L2compressionErrors)
print("compression relative errors H1 with nev ", str(nev), " = ", H1compressionErrors)

print("NIRB ONLINE DONE! ")



