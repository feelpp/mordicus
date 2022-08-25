# -*- coding: utf-8 -*-
## NIRB script python Online part 
## Elise Grosjean
## 01/2021

import os
import os.path as osp
import glob
import sys
import numpy as np
from pathlib import Path
import array
import warnings

from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Core.IO import StateIO as SIO

from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Modules.sorbonne.IO import VTKMeshReader as VTKMR
from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GmshMR
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import FFSolutionReader as FFSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW

from Mordicus.Modules.Safran.FE import FETools as FT
from BasicTools.FE import FETools as FT2
from BasicTools.FE.Fields.FEField import FEField

print("-----------------------------------")
print(" STEP II. 0: start Online nirb     ")
print("-----------------------------------")


#time=0.0 #steady
## Directories
currentFolder=os.getcwd()


# 3D Case
"""
OfflineResuFolder=osp.join(currentFolder,'3Dcase/3DData/FineSnapshots/') #folder for offline resu
FineDataFolder=osp.join(currentFolder,'3Dcase/3DData/FineSolution/') #folder for fine snapshots
CoarseDataFolder=osp.join(currentFolder,'3Dcase/3DData/CoarseSolution/') #folder for coarse snapshots
FineMeshFolder=osp.join(currentFolder,'3Dcase/3DData/FineMesh/') #folder for fine mesh (needed with Freefem snapshots)
CoarseMeshFolder=osp.join(currentFolder,'3Dcase/3DData/CoarseMesh/') #folder for coarse mesh (needed with Freefem)
OnlineResuFolder=osp.join(currentFolder,'3Dcase/3DData/FineSnapshots/') #folder for fine snapshots
"""

# 2D case

externalFolder=osp.join(currentFolder,'StationaryNS/External') #FreeFem scripts
OfflineResuFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineSnapshots/') #folder for offline resu
FineDataFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineSolution/') #folder for fine Solution (optional)
CoarseDataFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/CoarseSolution/') #folder for coarse solution
FineMeshFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineMesh/') #folder for fine mesh (needed with Freefem snapshots)
CoarseMeshFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/CoarseMesh/') #folder for coarse mesh (needed with Freefem)
OnlineResuFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineSnapshots/') #folder for offline resu

## Parameters

dimension=2 #dimension spatial domain
nbeOfComponentsPrimal = 2 # number of components 
FieldName="Velocity" #Snapshots fieldname
FieldNameExactSolution="u"#"Velocity" #Snapshots fieldname
Format= "FreeFem" # FreeFem or VTK
Method="Greedy" #POD or Greedy
Rectification=0 #1 with Rectification post-process (Coarse Snapshots required) or 0 without
ComputingError=1 # 1 if the fine solution is provided 
SavingApproximation=1 #if NIRB approximation saved

## Fine and coarse Solution files name
#coarseName="snapshotH0.vtu"
#fineName="snapshot0.vtu"

#########################################################
#                   LOAD DATA FOR ONLINE
#########################################################

collectionProblemData = SIO.LoadState(OfflineResuFolder+"collectionProblemData")
nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
l2ScalarProducMatrix = collectionProblemData.GetOperatorCompressionData("U")
h1ScalarProducMatrix=collectionProblemData.GetDataCompressionData("U")
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")

if Rectification == 1:
    R=collectionProblemData.GetDataCompressionData("Rectification")
    #print("Rectification matrix: ", R)

    
# ----------------------------------------------------------
# Converting the solutions to VTU if FreeFem format
if Format == "FreeFem": 
        FineMeshFileName=glob.glob(os.path.join(FineMeshFolder,"*.msh"))
        #assert len(FineMeshFileName)==1, "!! The user must provide only one fine mesh in the fine mesh folder !!"
        FineMeshFileName=FineMeshFileName[0]
        CoarseMeshFileName=glob.glob(os.path.join(CoarseMeshFolder,"*.msh"))
        #print(CoarseMeshFileName)
        
        #assert len(CoarseMeshFileName)==1, "!! The user must provide only one coarse mesh in the coarse mesh folder !!"
        CoarseMeshFileName=CoarseMeshFileName[0]

        if ComputingError==1:
            #print(FineDataFolder)
            FineSolutionFile=glob.glob(os.path.join(FineDataFolder,"*"))[0]
            print("read the fine solution in ", FineSolutionFile)
            suffix=str(Path(FineSolutionFile).suffix)
            if suffix == ".txt":
                FFFinetoVTKconvert=FFSR.FFSolutionReader(FieldName,FineMeshFileName)
                FFFinetoVTKconvert.FFReadToNp(externalFolder,FineSolutionFile) #create the solution with vtu format
        
        CoarseSnapshotsFile=glob.glob(os.path.join(CoarseDataFolder,"*.txt"))[0]
        FFCoarsetoVTKconvert=FFSR.FFSolutionReader(FieldName,CoarseMeshFileName);
        FFCoarsetoVTKconvert.FFReadToNp(externalFolder,CoarseSnapshotsFile) #create the coarse solution with vtu format
# ----------------------------------------------------------
# ----------------------------------------------------------
## MESH READER

## FINE MESH reader
if Format == "FreeFem":
        print(FineMeshFileName)
else:
        FineSnapshotFiles=sorted(glob.glob(os.path.join(FineDataFolder,"*.vtu")))
        FineMeshFileName=FineSnapshotFiles[0] #mesh from the snapshots
        #print(FineMeshFileName)

FineMeshReader=MR.MeshReader(FineMeshFileName,dimension)
FineMesh= FineMeshReader.ReadMesh()
print("Fine mesh defined in " + FineMeshFileName + " has been read")
numberOfNodes = FineMesh.GetNumberOfNodes()
print("number of nodes: ",numberOfNodes)

## COARSE MESH reader for rectification post-process

if Format == "FreeFem":
    print(CoarseMeshFileName)
else:
    CoarseSnapshotFiles=sorted(glob.glob(os.path.join(CoarseDataFolder,"*.vtu")))
    CoarseMeshFileName=CoarseSnapshotFiles[0] #mesh from the snapshots
                
CoarseMeshReader = MR.MeshReader(CoarseMeshFileName,dimension)
CoarseMesh = CoarseMeshReader.ReadMesh()
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")
numberOfNodes2 = CoarseMesh.GetNumberOfNodes()
print("number of nodes: ",numberOfNodes2)



# ----------------------------------------------------------
# ----------------------------------------------------------
# Interpolation on the fine mesh

option="basictools" #ff, basictools
if Format == "FreeFem":
    Folder=str(Path(FineMeshFileName).parents[0])
    stem=str(Path(FineMeshFileName).stem)
    suffix=str(Path(FineMeshFileName).suffix)
    if stem[-4:]!="GMSH":
        FineMeshFileName =  Folder+"/"+stem+"GMSH"+suffix
    Folder=str(Path(CoarseMeshFileName).parents[0])
    stem=str(Path(CoarseMeshFileName).stem)
    suffix=str(Path(CoarseMeshFileName).suffix)
    if stem[-4:]!="GMSH":
        CoarseMeshFileName =  Folder+"/"+stem+"GMSH"+suffix
operator=IOW.InterpolationOperator(FineDataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)
#operator=SIO.LoadState(FineDataFolder+"/Matrices/operator")
# ----------------------------------------------------------
# ----------------------------------------------------------
# READING COARSE SOLUTION

print("-----------------------------------")
print(" STEP I. 1: read coarse solution   ")
print("-----------------------------------")

CoarseSolutionFile=glob.glob(os.path.join(CoarseDataFolder,"*.vtu"))
print(CoarseSolutionFile)
assert len(CoarseSolutionFile)==1, "!! only one coarse solution needed in the coarse solution folder !!"
CoarseSolutionFile=CoarseSolutionFile[0]

VTKSnapshotReader=VTKSR.VTKSolutionReader(FieldName);
CoarseSolution =VTKSnapshotReader.VTKReadToNp(CoarseSolutionFile)#.flatten()
CoarseSolutionInterp=operator.dot(CoarseSolution).flatten()
solutionUHh=S.Solution("U",nbeOfComponentsPrimal,numberOfNodes,True)
solutionUHh.AddSnapshot(CoarseSolutionInterp,0)

onlineproblemData = PD.ProblemData("Online") #create online problem data
onlineproblemData.AddSolution(solutionUHh)

UnusedParam=-1 #Problem Data label
collectionProblemData.AddProblemData(onlineproblemData,unused=UnusedParam)

##################################################
# ONLINE COMPRESSION
##################################################

print("--------------------------------")
print(" STEP II. 2:  Online compression")
print("--------------------------------")

solutionUHh.CompressSnapshots(l2ScalarProducMatrix,reducedOrderBasisU)
CompressedSolutionU = solutionUHh.GetCompressedSnapshots()

if Rectification == 1:
    # Rectification

    coef=np.zeros(nev)
    for i in range(nev):
        coef[i]=0
        for j in range(nev):
            coef[i]+=R[i,j]*CompressedSolutionU[0][j]
        
    #print("coef without rectification: ", CompressedSolutionU[0])
    #print("coef with rectification ", coef)

    reconstructedCompressedSolution = np.dot(coef, reducedOrderBasisU) #with rectification

else:
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0

##################################################
# SAVE APPROXIMATION
##################################################
if SavingApproximation == 1:
    savedata=reconstructedCompressedSolution.reshape((numberOfNodes, nbeOfComponentsPrimal))
    
    if Format == "FreeFem":
        MeshBase = GmshMR.ReadGMSHBase(FineMeshFileName)
        SnapWrite=NpVTK.VTKWriter(MeshBase)
        SnapWrite.numpyToVTKSanpWriteFromGMSH(savedata,FieldName,osp.join(OnlineResuFolder,"NIRB_Approximation_"+str(nev)+".vtu"))

    else:
        MeshBase = VTKMR.ReadVTKBase(FineMeshFileName)
        SnapWrite=NpVTK.VTKWriter(MeshBase)
        SnapWrite.numpyToVTKSanpWrite(savedata,FieldName,osp.join(OnlineResuFolder,"NIRB_Approximation_"+str(nev)+".vtu"))


##################################################
# ONLINE ERRORS
##################################################
if ComputingError==1:
    
    print("-----------------------------------")
    print(" STEP II. 3: L2 and H1 errors      ")
    print("-----------------------------------")
    print("reading exact solution...")
    FineSolutionFile=glob.glob(os.path.join(FineDataFolder,"*.vtu"))
    assert len(FineSolutionFile)==1, "!! only one fine solution needed in the coarse solution folder !!"
    FineSolutionFile=FineSolutionFile[0]
    print(FineSolutionFile)
    VTKSnapshotReader=VTKSR.VTKSolutionReader(FieldNameExactSolution);
    exactSolution =VTKSnapshotReader.VTKReadToNp(FineSolutionFile).flatten()

    solutionU=S.Solution("U",nbeOfComponentsPrimal,numberOfNodes,True)
    solutionU.AddSnapshot(exactSolution,0) #only one snapshot->time=0

    problemData = PD.ProblemData("Online")
    problemData.AddSolution(solutionU)
    collectionProblemData.AddProblemData(problemData,unused=UnusedParam)
    
    exactSolution =solutionU.GetSnapshot(0)
    #solutionU.CompressSnapshots(l2ScalarProducMatrix,reducedOrderBasisU)

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



