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
from Mordicus.Core.IO import StateIO as SIO
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array
import sys

nev=int(sys.argv[1])#11   #nombre de modes
ns=22#nombre de snapshots
time=0.0 
dimension=3
print("NIRB online...")
## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'StationaryNSData')
print("data in" + dataFolder)
parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds

## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')

print("-----------------------------------")
print(" STEP2: start Online nirb          ")
print("-----------------------------------")

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################
collectionProblemData = SIO.LoadState("collectionProblemData")
snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")
h1ScalarProducMatrix=SIO.LoadState("h1ScalarProducMatrix")
R=collectionProblemData.GetDataCompressionData("Rectification")
print(R)
operatorCompressionData = collectionProblemData.GetOperatorCompressionData() #l2ScalarProducMatrix
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")

#### LOAD FINE MESH
print("reading fine mesh")
meshFileName=dataFolder+"/mesh1.vtu"
meshReader = MR.MeshReader(meshFileName)
mesh = meshReader.ReadMesh()
mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes
print("Mesh defined in " + meshFileName + " has been read")

nbeOfComponentsPrimal = 3 # vitesses 3D
numberOfNodes = mesh.GetNumberOfNodes()

#### LOAD COARSE MESH
VTKmesh2 = dataFolder + "/mesh2.vtu"
meshReader2=MR.MeshReader(VTKmesh2)
mesh2 = meshReader2.ReadMesh()
mesh2.GetInternalStorage().nodes = mesh2.GetInternalStorage().nodes


    ##################################################
    #### Interpolation coarse solution into fine mesh (using Basictools)
    ##################################################
"""
#coarse mesh
inputmesh=FT.ConvertMeshToUnstructuredMesh(mesh2)
space, numberings, _offset, _NGauss = FT2.PrepareFEComputation(inputmesh)
inputFEField =FEField(name="field",mesh=inputmesh,space=space,numbering=numberings[0])
#reading coarse solution
test=VTKSR.VTKSolutionReader("Velocity");
coarseFile=dataFolder+"/uHgrossier"+str(0)
u1_np_array_coarse =test.VTKReadToNp(dataFolder+"/uHgrossier",0) #solution sous la forme uHgrossier0.vtu
print("coarse solution in "+ coarseFile + "has been read")
print("coarse solution shape", np.shape(u1_np_array_coarse))
#Fine mesh
outmesh=FT.ConvertMeshToUnstructuredMesh(mesh)
outnodes = outmesh.nodes
methods = ["Interp/Nearest","Nearest/Nearest","Interp/Clamp","Interp/Extrap"]
method = methods[2]
operator, status = GetFieldTransferOp(inputFEField,outnodes,method = method,verbose=True) #interpolation!
#Compute the projected data using the projection operator
newdata = operator.dot(u1_np_array_coarse)
print("interpolated solution shape" , np.shape(newdata))
VTKBase = MR.ReadVTKBase(dataFolder+"/mesh1.vtu")
SnapWrite=NpVTK.VTKWriter(VTKBase)
SnapWrite.numpyToVTKSanpWrite(newdata)
"""

test=VTKSR.VTKSolutionReader("Velocity");
newdata =test.VTKReadToNp(dataFolder+"/RecSol",0)
newdata=newdata.flatten()


#Instancie la solution
solutionUH=S.Solution("U",dimension,numberOfNodes,True)
solutionUH.AddSnapshot(newdata,0)
onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUH)
Newparam=110.0 #parameters[ns-1]
collectionProblemData.AddProblemData(onlineproblemData,mu1=Newparam)

l2ScalarProducMatrix = snapshotCorrelationOperator
#verification base orthonormee....
"""
for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        print(i,j," ",norm)
"""

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
"""
VTKBase = MR.ReadVTKBase(dataFolder+"/mesh1.vtu")
SnapWrite=NpVTK.VTKWriter(VTKBase)
SnapWrite.numpyToVTKSanpWrite(reconstructedCompressedSolution,"approximation"+str(nev)+".vtu")
"""
    ##################################################
    # ONLINE ERRORS
    ##################################################
print("-----------------------------------")
print(" STEP4: L2 and H1 errors           ")
print("-----------------------------------")

print("reading exact solution...")
test=VTKSR.VTKSolutionReader("Velocity");
u1_np_array =test.VTKReadToNp(dataFolder+"/snapshot",ns)
#instancie une solution
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



