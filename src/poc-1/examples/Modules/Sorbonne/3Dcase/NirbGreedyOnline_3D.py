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
from BasicTools.FE.Fields.FEField import FEField
from BasicTools.Containers import Filters
from BasicTools.Containers.UnstructuredMeshFieldOperations import GetFieldTransferOp
from Mordicus.Modules.CT.IO import VTKSolutionReader as VTKSR
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

print("NIRB online...")

## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'3DData')

ns=1 #number of snapshots

for root, _, files in os.walk(dataFolder+"/FineSnapshots/"):
    print("number of snapshots in ", root, ": ",len(files))
    ns=len(files)
    print("number of snapshots: ",ns)
    
##################################################
# LOAD DATA FOR ONLINE
##################################################

collectionProblemData = SIO.LoadState(dataFolder+"/OFFLINE_RESU/collectionProblemData")
#snapshotCorrelationOperator = SIO.LoadState(dataFolder+"/Matrices/snapshotCorrelationOperator")
#h1ScalarProducMatrix=SIO.LoadState(dataFolder+"/Matrices/h1ScalarProducMatrix")
nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
assert nev<=ns, " !! To many number of modes, nev must be less than ns !!"
operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")
R=collectionProblemData.GetDataCompressionData("Rectification")
#print("Rectification matrix: ", R)

#### LOAD FINE MESH
print("reading fine mesh")
#FineMeshFileName=dataFolder+"/FineMesh/fineMesh.vtu"
FineMeshFileName=dataFolder+"/FineSolution/snapshot0.vtu"
meshReader = MR.MeshReader(FineMeshFileName)
fineMesh = meshReader.ReadMesh()
fineMesh.GetInternalStorage().nodes = fineMesh.GetInternalStorage().nodes
print("Fine mesh defined in " + FineMeshFileName + " has been read")

nbeOfComponentsPrimal = 3 # vitesses 3D
numberOfNodes = fineMesh.GetNumberOfNodes()

l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(fineMesh, 3)
h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(fineMesh, 3)
snapshotCorrelationOperator=l2ScalarProducMatrix #mass matrix

#### LOAD COARSE MESH
#CoarseMeshFileName=dataFolder+"/CoarseMesh/coarseMesh.vtu"
CoarseMeshFileName=dataFolder+"/CoarseSolution/snapshotH0.vtu"
meshReader = MR.MeshReader(CoarseMeshFileName)
coarseMesh = meshReader.ReadMesh()
coarseMesh.GetInternalStorage().nodes = coarseMesh.GetInternalStorage().nodes
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")


print("-------------------------------------------------")
print(" STEP II. 1: Read and interpolate Coarse Solution")
print("-------------------------------------------------")

##################################################
#### Interpolation coarse solution into fine mesh (using Basictools)
##################################################

## FreeFem++ or basictools interpolation

option="basictools" #ff or basictools
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,option=option)
#operator=SIO.LoadState(dataFolder+"/Matrices/operator")


#Reading coarse solution
VTKSnapshotReader=VTKSR.VTKSolutionReader("Velocity");
CoarseSolutionFolder=osp.join(dataFolder,'CoarseSolution')
uH_np_array =VTKSnapshotReader.VTKReadToNp(dataFolder+"/CoarseSolution/snapshotH",0) #solution sous la forme snapshotH+str(ns).vtu

print("coarse solution in "+ CoarseSolutionFolder + " has been read ")

#Compute the projected data using the interpolation operator
if option=="ff":
    uH_np_array=uH_np_array.flatten() 
    
uHh = operator.dot(uH_np_array) #interpolation

if option=="ff":
   uHh=uHh.reshape((numberOfNodes, 3)) #if ff

"""  
# save interpolated solution

VTKBase = MR.ReadVTKBase(FineMeshFileName)
SnapWrite=NpVTK.VTKWriter(VTKBase)
SnapWrite.numpyToVTKSanpWrite(uHh,dataFolder+"/CoarseSolutionInterp/uHh.vtu")

# read interpolated solution
uHh =VTKSnapshotReader.VTKReadToNp(dataFolder+"/CoarseSolutionInterp/uHh",0)

"""

uHh=uHh.flatten()
solutionUHh=S.Solution("U",dimension,numberOfNodes,True)
solutionUHh.AddSnapshot(uHh,0)

onlineproblemData = PD.ProblemData("Online")

onlineproblemData.AddSolution(solutionUHh)

UnusedParam=0 #parameters[ns-1]
collectionProblemData.AddProblemData(onlineproblemData,mu=UnusedParam)

l2ScalarProducMatrix = snapshotCorrelationOperator #Mass Matrix


##################################################
# ONLINE COMPRESSION
##################################################

print("--------------------------------")
print(" STEP II. 2:  Online compression")
print("--------------------------------")

solutionUHh.CompressSnapshots(snapshotCorrelationOperator,reducedOrderBasisU)
CompressedSolutionU = solutionUHh.GetCompressedSnapshots()

#Rectification

coef=np.zeros(nev)
for i in range(nev):
    coef[i]=0
    for j in range(nev):
        coef[i]+=R[i,j]*CompressedSolutionU[0][j]
        
print("coef without rectification: ", CompressedSolutionU[0])
print("coef with rectification ", coef)

reconstructedCompressedSolution = np.dot(coef, reducedOrderBasisU) #with rectification
#reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0


##################################################
# SAVE APPROXIMATION
##################################################

VTKBase = MR.ReadVTKBase(FineMeshFileName)
SnapWrite=NpVTK.VTKWriter(VTKBase)
savedata=reconstructedCompressedSolution.reshape((numberOfNodes, 3)) #if ff
SnapWrite.numpyToVTKSanpWrite(savedata,dataFolder+"/ONLINE_RESU/NIRB_Greedy_Approximation_"+str(nev)+".vtu")
print("approximation saved in ",dataFolder+"/ONLINE_RESU/NIRB_Greedy_Approximation_"+str(nev))

##################################################
# ONLINE ERRORS
##################################################

print("-----------------------------------")
print(" STEP II. 3: L2 and H1 errors      ")
print("-----------------------------------")

print("reading exact solution...")

u_np_array =VTKSnapshotReader.VTKReadToNp(dataFolder+"/FineSolution/snapshot",0)
u_np_array=u_np_array.flatten()

solutionU=S.Solution("U",dimension,numberOfNodes,True)
solutionU.AddSnapshot(u_np_array,0) #only one snapshot->time=0

problemData = PD.ProblemData(dataFolder)
problemData.AddSolution(solutionU)
collectionProblemData.AddProblemData(problemData,mu=UnusedParam)
    
exactSolution =solutionU.GetSnapshot(0)
solutionU.CompressSnapshots(snapshotCorrelationOperator,reducedOrderBasisU)
CompressedSolutionU = solutionU.GetCompressedSnapshots()
reconstructedCompressedSolutionh = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0

#relative errors list
L2compressionErrors=[]
H1compressionErrors=[]

norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))

t=solutionUHh.GetSnapshot(0)-exactSolution
normh1rel=np.sqrt(t@l2ScalarProducMatrix@t)/norml2ExactSolution
print("H1 Projection error without NIRB: " , normh1rel)

if norml2ExactSolution != 0:
    err=reconstructedCompressedSolution-exactSolution
    errh=reconstructedCompressedSolutionh-exactSolution
    L2relError=np.sqrt(err@(l2ScalarProducMatrix@err))/norml2ExactSolution
    H1relError=np.sqrt(err@h1ScalarProducMatrix@err)/normh1ExactSolution
    H1relErrorh=np.sqrt(errh@h1ScalarProducMatrix@errh)/normh1ExactSolution
    value = [nev,H1relError]
    valueh = [nev,H1relErrorh]
    f = open("NIRB_Greedy_errorH1.txt", "a")
    f.write(str(value))
    f.close()
    f2 = open("NIRB_Greedy_errorH1_h.txt", "a")
    f2.write(str(valueh))
    f2.close()

else:
    print("norm exact solution = 0")
    err=reconstructedCompressedSolution-exactSolution
    L2relError=np.sqrt(err@(l2ScalarProducMatrix@err))
    
    
L2compressionErrors.append(L2relError)
H1compressionErrors.append(H1relError)

print("compression relative errors L2 =", L2compressionErrors)
print("compression relative errors H1 =", H1compressionErrors)

print("NIRB ONLINE DONE! ")



