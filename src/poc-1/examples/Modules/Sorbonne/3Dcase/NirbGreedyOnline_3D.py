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
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array

ns=22 #number of snapshots
time=0.0 
dimension=3
print("NIRB online...")
## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'3DData')
#parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds

## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')

print("-----------------------------------")
print(" STEP2: start Online nirb        ")
print("-----------------------------------")

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################
collectionProblemData = SIO.LoadState(dataFolder+"/OFFLINE_RESU/collectionProblemData")
snapshotCorrelationOperator = SIO.LoadState(dataFolder+"/Matrices/snapshotCorrelationOperator")
h1ScalarProducMatrix=SIO.LoadState(dataFolder+"/Matrices/h1ScalarProducMatrix")
nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")
R=collectionProblemData.GetDataCompressionData("Rectification")
#print("R ", R)

#### LOAD FINE MESH
print("reading fine mesh")
meshFileName=dataFolder+"/FineMesh/mesh1.vtu"
meshReader = MR.MeshReader(meshFileName)
mesh = meshReader.ReadMesh()
mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes
print("Mesh defined in " + meshFileName + " has been read")

nbeOfComponentsPrimal = 3 # vitesses 3D
numberOfNodes = mesh.GetNumberOfNodes()

#### LOAD COARSE MESH
VTKmesh2 = dataFolder + "/CoarseMesh/mesh2.vtu"
meshReader2=MR.MeshReader(VTKmesh2)
mesh2 = meshReader2.ReadMesh()
mesh2.GetInternalStorage().nodes = mesh2.GetInternalStorage().nodes


    ##################################################
    #### Interpolation coarse solution into fine mesh (using Basictools)
    ##################################################

## ff si mesh en vtk, et sinon basictools
finemesh=dataFolder+"/FineMesh/mesh1.vtu" #if basictools
coarsemesh=dataFolder+"/CoarseMesh/mesh2.vtu"
#inputmesh=dataFolder + "/FineMesh/mesh1.vtk" #if ff
#outputmesh=dataFolder + "/CoarseMesh/mesh2.vtk"
option="basictools" #ff or basictools

#IOW.InterpolationOperator(dataFolder,finemesh,coarsemesh,option=option)
operator=SIO.LoadState(dataFolder+"/Matrices/operator")

#reading coarse solution
test=VTKSR.VTKSolutionReader("Velocity");
coarseFile=dataFolder+"/uHgrossier"+str(0)
u1_np_array_coarse =test.VTKReadToNp(dataFolder+"/CoarseSolution/uHgrossier",0) #solution sous la forme uHgrossier0.vtu

print("coarse solution in "+ coarseFile + "has been read ")
print("coarse solution shape ", np.shape(u1_np_array_coarse))

#Compute the projected data using the interpolation operator
if option=="ff":
    u1_np_array_coarse=u1_np_array_coarse.flatten() #if ff interp
    
newdata = operator.dot(u1_np_array_coarse)
print("interpolated solution shape " , np.shape(newdata))

if option=="ff":
   newdata=newdata.reshape((numberOfNodes, 3)) #if ff

#save interpolated solution
VTKBase = MR.ReadVTKBase(dataFolder+"/FineMesh/mesh1.vtu")
SnapWrite=NpVTK.VTKWriter(VTKBase)
SnapWrite.numpyToVTKSanpWrite(newdata,dataFolder+"/CoarseSolutionInterp/uH0.vtu")

#read interpolated solution
test=VTKSR.VTKSolutionReader("Velocity");
newdata =test.VTKReadToNp(dataFolder+"/CoarseSolutionInterp/uH",0)
newdata=newdata.flatten()

solutionUH=S.Solution("U",dimension,numberOfNodes,True)
solutionUH.AddSnapshot(newdata,0)
onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUH)
Newparam=110.0 #parameters[ns-1]
collectionProblemData.AddProblemData(onlineproblemData,mu1=Newparam)

l2ScalarProducMatrix = snapshotCorrelationOperator


    ##################################################
    # ONLINE COMPRESSION
    ##################################################
print("-----------------------------------")
print(" STEP3: Snapshot compression       ")
print("-----------------------------------")        
solutionUH.CompressSnapshots(snapshotCorrelationOperator,reducedOrderBasisU)
CompressedSolutionU = solutionUH.GetCompressedSnapshots()
#Rectification
coef=np.zeros(nev)
for i in range(nev):
    coef[i]=0
    for j in range(nev):
        coef[i]+=R[i,j]*CompressedSolutionU[0][j]
        
print("coef without rectif ", CompressedSolutionU[0])
print("coef with rectif ", coef)
reconstructedCompressedSolution = np.dot(coef, reducedOrderBasisU) #with rectif
#reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    ##################################################
    # SAVE APPROXIMATION
    ##################################################

VTKBase = MR.ReadVTKBase(dataFolder+"/FineMesh/mesh1.vtu")
SnapWrite=NpVTK.VTKWriter(VTKBase)
SnapWrite.numpyToVTKSanpWrite(reconstructedCompressedSolution,dataFolder+"/ONLINE_RESU/approximation"+str(nev)+".vtu")

    ##################################################
    # ONLINE ERRORS
    ##################################################
print("-----------------------------------")
print(" STEP4: L2 and H1 errors           ")
print("-----------------------------------")

print("reading exact solution...")
test=VTKSR.VTKSolutionReader("Velocity");
u1_np_array =test.VTKReadToNp(dataFolder+"/FineSolution/snapshot",ns)
u1_np_array=u1_np_array.flatten()

solutionU=S.Solution("U",dimension,numberOfNodes,True)
solutionU.AddSnapshot(u1_np_array,0) #only one snapshot->time=0

problemData = PD.ProblemData(dataFolder)
problemData.AddSolution(solutionU)
collectionProblemData.AddProblemData(problemData,mu1=110.0)
    
exactSolution =solutionU.GetSnapshot(0)

solutionU.CompressSnapshots(snapshotCorrelationOperator,reducedOrderBasisU)
CompressedSolutionU = solutionU.GetCompressedSnapshots()
reconstructedCompressedSolutionh = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0

#error list
compressionErrors=[]
h1compressionErrors=[]

norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))

t=solutionUH.GetSnapshot(0)-exactSolution
normh1rel=np.sqrt(t@l2ScalarProducMatrix@t)/norml2ExactSolution
print("Projection error without NIRB" , normh1rel)

if norml2ExactSolution != 0:
    t=reconstructedCompressedSolution-exactSolution
    t1=reconstructedCompressedSolutionh-exactSolution
    relError=np.sqrt(t@(l2ScalarProducMatrix@t))/norml2ExactSolution
    relh1Error=np.sqrt(t@h1ScalarProducMatrix@t)/normh1ExactSolution
    relh1Errorh=np.sqrt(t1@h1ScalarProducMatrix@t1)/normh1ExactSolution
    value = [nev,relh1Error]
    valueh = [nev,relh1Errorh]
    f = open("errorH1.txt", "a")
    f.write(str(value))
    f.close()
    f2 = open("errorH1h.txt", "a")
    f2.write(str(valueh))
    f2.close()

else:
    print("exact solution =0")
    relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    
compressionErrors.append(relError)
h1compressionErrors.append(relh1Error)
print("compressionErrors =", compressionErrors)
print("compressionErrorsh1 =", h1compressionErrors)
print("NIRB ONLINE DONE")



