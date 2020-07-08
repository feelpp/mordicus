import os
import os.path as osp

import subprocess

from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT
from  Mordicus.Modules.CT.IO import VTKSolutionReader as VTKSR
from initCase import initproblem
from initCase import basisFileToArray
import numpy as np
from pathlib import Path
import array


nev=5    #nombre de modes
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
uH=osp.join(dataFolder,'soluH.txt')

print("-----------------------------------")
print(" STEP2: start Online nirb        ")
print("-----------------------------------")

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################

collectionProblemData = CPD.LoadState("mordicusState")
operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
snapshotCorrelationOperator = collectionProblemData.GetSnapshotCorrelationOperator("U")
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")

#Fine mesh
meshFileNameGMSH=dataFolder +"/mesh1GMSH.msh"
meshReader = GMR.GmshMeshReader(meshFileNameGMSH)
mesh = meshReader.ReadMesh()
mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes[:,:2]

print("Mesh defined in " + meshFileNameGMSH + " has been read")
nbeOfComponentsPrimal = 2 # vitesses 2D
numberOfNodes = mesh.GetNumberOfNodes()

#Coarse mesh
meshFileName2 = dataFolder + "/mesh2.msh"
meshFileNameGMSH2 = dataFolder + "/mesh2GMSH.msh"
print(meshFileName2)
GMR.CheckAndConvertMeshFFtoGMSH(meshFileName2,meshFileNameGMSH2)
print(" read mesh ok...")

#lecture snapshot grossier
test=VTKSR.VTKSolutionReader("u");

# Interpolation Solution maillage grossier vers maillage fin (FF ou Basictools)
scriptFreeFemInterpolation=osp.join(externalFolder,'FF_Interpolation.edp')
try:
    FNULL = open(os.devnull, 'w')
    ret = subprocess.run(["FreeFem++", scriptFreeFemInterpolation,
                          "-m1"   , meshFileNameGMSH,
                          "-m2"   , meshFileNameGMSH2,
                          "-u", uH,
                          "-outputDir", dataFolder
                          ],
                          stdout=FNULL,
                          stderr=subprocess.PIPE)
    ret.check_returncode()
except subprocess.CalledProcessError:
    retstr = "Error when calling Freefem++, interpolation script\n" + "    Returns error:\n" + str(ret.stderr)
    raise OSError(ret.returncode, retstr)


u1_np_array_coarse =test.VTKReadToNp(dataFolder+"/uH",0)
#instancie une solution
u1_np_array_coarse_interpol=u1_np_array_coarse.flatten()

solutionUH=S.Solution("U",dimension,numberOfNodes,True)

### ajouter la snapshot A solutionU
solutionUH.AddSnapshot(u1_np_array_coarse_interpol,0)
onlineproblemData = PD.ProblemData("Online")
onlineproblemData.AddSolution(solutionUH)
Newparam=110.0 #parameters[ns-1]
collectionProblemData.AddProblemData(onlineproblemData,mu1=Newparam)
 #on ajoute la solution à la collection de pb initiale
l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
 #verification base orthonormee....
for i in range(5):
        reducedOrderBasisUNorm=np.linalg.norm(reducedOrderBasisU[i,:])
        #reducedOrderBasisU[i,:]/=reducedOrderBasisUNorm
for i in range(5):
    for j in range(5):
        if i==j:
            print(i,"norm?",np.linalg.norm(reducedOrderBasisU[i,:]))
        else:
            u11=np.array(reducedOrderBasisU[i,:])
            u21=np.array(reducedOrderBasisU[j,:])
            matVecProduct = l2ScalarProducMatrix.dot(u11)
            a = np.dot(matVecProduct, u21)
            print(i,j,"ortho?:",a)
            
    ##################################################
    # ONLINE COMPRESSION
    ##################################################
print("-----------------------------------")
print(" STEP3: Snapshot compression       ")
print("-----------------------------------")        
solutionUH.CompressSnapshots(snapshotCorrelationOperator,reducedOrderBasisU)
CompressedSolutionU = solutionUH.GetCompressedSnapshots()
reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    ##################################################
    # ONLINE ERRORS
    ##################################################
print("-----------------------------------")
print(" STEP4: L2 and H1 errors           ")
print("-----------------------------------")


print("reading exact solution...")
test=VTKSR.VTKSolutionReader("u");
u1_np_array =test.VTKReadToNp(dataFolder+"/snapshot",ns-1)
 
#instancie une solution
u1_np_array=u1_np_array.flatten()

solutionU=S.Solution("U",dimension,numberOfNodes,True)
### Only one snapshot --> time 0 
solutionU.AddSnapshot(u1_np_array,0)
problemData = PD.ProblemData(dataFolder)
problemData.AddSolution(solutionU)
collectionProblemData.AddProblemData(problemData,mu1=110.0)
    
#problemData=collectionProblemData.GetProblemData(mu1=110.0)
#solutionU=problemData.GetSolution("U")
#print(solutionU)
exactSolution =solutionU.GetSnapshot(0)
compressionErrors=[]
    
norml2ExactSolution = np.linalg.norm(exactSolution)
if norml2ExactSolution != 0:
    print("rec",np.linalg.norm(reconstructedCompressedSolution))
    print("rec",np.linalg.norm(exactSolution))
    relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
else:
    relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
compressionErrors.append(relError)
print("compressionErrors =", compressionErrors)


""" 
----------------------------
              PLOT SOL
----------------------------
""" 
"""
solutionFile = osp.join(os.getcwd(),'../test/data/solution.txt')
"""

"""
Plot the solution with FF++

Arguments:
    meshFile (str): path to .msh file containing mesh
    solution (str): path to .txt file containing snapshots

"""

"""
#from tempfile import NamedTemporaryFile
#with NamedTemporaryFile(delete=True) as f:
#    tmpbase = f.name
import subprocess
# The following should be executed with python > 3.5
import os
import os.path as osp

scriptFreeFem=osp.join(externalFolder,'PlotSol.edp')
try:
    ret = subprocess.run(["FreeFem++", scriptFreeFem,
                          "-m1"   , meshFile1,
                          "-uh", uh],
                          stderr=subprocess.PIPE)
    ret.check_returncode()
except subprocess.CalledProcessError:
    retstr = "Error when calling Freefem++\n" + "    Returns error:\n" + str(ret.stderr)
    raise OSError(ret.returncode, retstr)

#return 0
"""

