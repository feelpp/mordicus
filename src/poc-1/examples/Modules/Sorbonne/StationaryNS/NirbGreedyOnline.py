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


FineSnapshotFiles=sorted(glob.glob(dataFolder+"/snapshots_*"))
#print(FineSnapshotFiles)
print("number of snapshots in ", dataFolder, ": ",len(FineSnapshotFiles))
ns=len(FineSnapshotFiles)  #number of snapshots
parameters = range(ns)#for problemdata

## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')

#scriptFreeFem=osp.join(externalFolder,'FFtoVTK.edp')

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
R=collectionProblemData.GetDataCompressionData("rectification")
print("R",R)
### Fine mesh
FieldName="u"

FineMeshFileName=dataFolder +"/mesh1GMSH.msh"
FineMeshReader=MR.MeshReader(FineMeshFileName,dimension)
FineMesh= FineMeshReader.ReadMesh()

print("Mesh defined in " + FineMeshFileName + " has been read")
nbeOfComponentsPrimal = 2 #number of components
numberOfNodes = FineMesh.GetNumberOfNodes()

## Coarse mesh
CoarseMeshFileName = dataFolder + "/mesh2GMSH.msh"
CoarseMeshReader=MR.MeshReader(CoarseMeshFileName,dimension)
CoarseMesh= CoarseMeshReader.ReadMesh()

#coarse solution
SnapshotsReader=VTKSR.VTKSolutionReader(FieldName);

# FF Interpolation with FF++
"""
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
"""
option="basictools"
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)

FFCoarseFileName=osp.join(dataFolder,'soluH.txt')
FFmesh=osp.join(dataFolder,'mesh2.msh')
FFCoarsetoVTKconvert=FFSR.FFSolutionReader(FieldName,FFmesh);
FFCoarsetoVTKconvert.FFReadToNp(FFCoarseFileName) #create the coarse solution with vtu format
#CoarseFileName=dataFolder+"/uH0.vtu"
CoarseFileName=dataFolder+"/"+str(Path(FFCoarseFileName).stem)+"_"+str(0)+".vtu"
CoarseSolution =SnapshotsReader.VTKReadToNp(CoarseFileName)
CoarseSolution=operator.dot(CoarseSolution).flatten() #coarse snapshot interpolated

solutionUH=S.Solution("U",dimension,numberOfNodes,True)

### ajouter la snapshot A solutionU
solutionUH.AddSnapshot(CoarseSolution,0)#time =0
onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUH)
Newparam=ns
collectionProblemData.AddProblemData(onlineproblemData,unused=Newparam)

#l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
#l2ScalarProducMatrix=snapshotCorrelationOperator
h1ScalarProducMatrix= FT.ComputeH10ScalarProductMatrix(FineMesh, 2)
            
    ##################################################
    # ONLINE COMPRESSION
    ##################################################
print("-----------------------------------")
print(" STEP3: Snapshot compression       ")
print("-----------------------------------")        
solutionUH.CompressSnapshots(l2ScalarProducMatrix,reducedOrderBasisU)
CompressedSolutionU = solutionUH.GetCompressedSnapshots()
coef=np.zeros(nev) #+rectification
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
FineSolutionFileName=dataFolder+"/snapshot"+str(ns-1)+".vtu"
FineSolution =SnapshotsReader.VTKReadToNp(FineSolutionFileName).flatten()

solutionU=S.Solution("U",dimension,numberOfNodes,True)
solutionU.AddSnapshot(FineSolution,0)# Only one snapshot --> time 0
problemData = PD.ProblemData(dataFolder)
problemData.AddSolution(solutionU)
collectionProblemData.AddProblemData(problemData,unused=ns)
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
