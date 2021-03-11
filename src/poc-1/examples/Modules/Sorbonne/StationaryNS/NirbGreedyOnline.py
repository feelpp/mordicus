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
from  Mordicus.Modules.CT.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Core.IO import StateIO as SIO
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array


ns=10
time=0.0 
dimension=2
print("NIRB online...")
## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'StationaryNSData')
parameters = [float(1+15*i) for i in range(ns)]   ###Reynolds

## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')

#scriptFreeFem=osp.join(externalFolder,'FFtoVTK.edp')
uH=osp.join(dataFolder+"/CoarseSolution/",'soluH.txt')

print("-----------------------------------")
print(" STEP2: start Online nirb          ")
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
R=collectionProblemData.GetDataCompressionData(dataFolder+"/OFFLINE_RESU/Rectification")
print("R",R)
### Fine mesh

meshFileName=dataFolder +"/FilesForFFInterp/mesh1GMSH.msh"
if str(Path(meshFileName).suffix)=="vtu":
    meshReader=MR.MeshReader(meshFileName)
else:
    meshReader = GMR.GmshMeshReader(meshFileName)
    
mesh = meshReader.ReadMesh()
mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes[:,:2]

print("Mesh defined in " + meshFileName + " has been read")
nbeOfComponentsPrimal = 2 # vitesses 2D
numberOfNodes = mesh.GetNumberOfNodes()

## Coarse mesh
meshFileName2 = dataFolder + "/CoarseMesh/mesh2.msh"
meshFileNameGMSH2 = dataFolder + "/FilesForFFInterp/mesh2GMSH.msh"
print(meshFileName2)

GMR.CheckAndConvertMeshFFtoGMSH(meshFileName2,meshFileNameGMSH2)
print(" read coarse mesh ok...")

#coarse solution
test=VTKSR.VTKSolutionReader("u");

# FF Interpolation with FF++
scriptFreeFemInterpolation=osp.join(externalFolder,'FF_Interpolation.edp')
try:
    FNULL = open(os.devnull, 'w')
    ret = subprocess.run(["FreeFem++", scriptFreeFemInterpolation,
                          "-m1"   , meshFileName,
                          "-m2"   , meshFileNameGMSH2,
                          "-u", uH,
                          "-outputDir", dataFolder+"/CoarseSolutionInterp"
                          ],
                          stdout=FNULL,
                          stderr=subprocess.PIPE)
    ret.check_returncode()
except subprocess.CalledProcessError:
    retstr = "Error when calling Freefem++, interpolation script\n" + "    Returns error:\n" + str(ret.stderr)
    raise OSError(ret.returncode, retstr)

u1_np_array_coarse =test.VTKReadToNp(dataFolder+"/CoarseSolutionInterp/uH",0)
#instancie une solution
u1_np_array_coarse=u1_np_array_coarse.flatten()
solutionUH=S.Solution("U",dimension,numberOfNodes,True)
### ajouter la snapshot A solutionU
solutionUH.AddSnapshot(u1_np_array_coarse,0)
onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUH)
Newparam=110.0 #parameters[ns-1]
collectionProblemData.AddProblemData(onlineproblemData,mu1=Newparam)

#l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
l2ScalarProducMatrix=snapshotCorrelationOperator

            
    ##################################################
    # ONLINE COMPRESSION
    ##################################################
print("-----------------------------------")
print(" STEP3: Snapshot compression       ")
print("-----------------------------------")        
solutionUH.CompressSnapshots(snapshotCorrelationOperator,reducedOrderBasisU)
CompressedSolutionU = solutionUH.GetCompressedSnapshots()
coef=np.zeros(nev)
for i in range(nev):
    for j in range(nev):
        coef[i]+=R[i,j]*CompressedSolutionU[0][j]
reconstructedCompressedSolution = np.dot(coef, reducedOrderBasisU) #pas de tps 0
print("coef without rectif ", CompressedSolutionU[0])
print("coef with rectif ", coef)
#reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    ##################################################
    # ONLINE ERRORS
    ##################################################
print("-----------------------------------")
print(" STEP4: L2 and H1 errors           ")
print("-----------------------------------")

print("reading exact solution...")
test=VTKSR.VTKSolutionReader("u");
u1_np_array =test.VTKReadToNp(dataFolder+"/FineSolution/snapshot",ns-1)
#instancie une solution
u1_np_array=u1_np_array.flatten()

solutionU=S.Solution("U",dimension,numberOfNodes,True)
solutionU.AddSnapshot(u1_np_array,0)# Only one snapshot --> time 0
problemData = PD.ProblemData(dataFolder)
problemData.AddSolution(solutionU)
collectionProblemData.AddProblemData(problemData,mu1=110.0)
exactSolution =solutionU.GetSnapshot(0)
compressionErrors=[]
H1compressionErrors=[]
norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))

if norml2ExactSolution != 0:
    t=reconstructedCompressedSolution-exactSolution
    relError=np.sqrt(t@l2ScalarProducMatrix@t)/norml2ExactSolution
    relH1Error=np.sqrt(t@h1ScalarProducMatrix@t)/normh1ExactSolution
   
else:
    relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
H1compressionErrors.append(relH1Error)
compressionErrors.append(relError)
print("H1compressionErrors =", H1compressionErrors)
print("L2compressionErrors =", compressionErrors)
