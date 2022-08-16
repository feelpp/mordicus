# -*- coding: utf-8 -*-
## NIRB script python Offline part 
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
import feelpp 



from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Core.IO import StateIO as SIO

from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Modules.Safran.FE import FETools as FT
#from BasicTools.FE import FETools as FT2
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import FFSolutionReader as FFSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
from Mordicus.Modules.sorbonne.MOR import Greedy as GD



## Directories
currentFolder=os.getcwd()
dataFolder = osp.expanduser("~/feelppdb/nirb/")
modelFolder = "StationaryNS/" # or "heat"

"""
# 3D Case
OfflineResuFolder=osp.join(currentFolder,'3Dcase/3DData/FineSnapshots/') #folder for offline resu
FineDataFolder=osp.join(currentFolder,'3Dcase/3DData/FineSnapshots/') #folder for fine snapshots
CoarseDataFolder=osp.join(currentFolder,'3Dcase/3DData/CoarseSnapshots/') #folder for coarse snapshots
FineMeshFolder=osp.join(currentFolder,'3Dcase/3DData/FineMesh/') #folder for fine mesh (needed with Freefem snapshots)
CoarseMeshFolder=osp.join(currentFolder,'3Dcase/3DData/CoarseMesh/') #folder for coarse mesh (needed with Freefem)

"""
# 2D case

# externalFolder=osp.join(currentFolder,'models/StationaryNS/External') #FreeFem scripts
# OfflineResuFolder=osp.join(dataFolder,modelFolder,'FineSnapshots/') #folder for offline resu
# FineDataFolder=osp.join(dataFolder,modelFolder,'FineSnapshots/') #folder for fine snapshots
# CoarseDataFolder=osp.join(dataFolder,modelFolder,'CoarseSnapshots/') #folder for coarse snapshots
# FineMeshFolder=osp.join(dataFolder,modelFolder,'FineMesh/') #folder for fine mesh (needed with Freefem snapshots)
# CoarseMeshFolder=osp.join(dataFolder,modelFolder,'CoarseMesh/') #folder for coarse mesh (needed with Freefem)

## Parameters

dimension=2 #dimension spatial domain
nbeOfComponentsPrimal = 2 # number of components 
FieldName="Velocity" #Snapshots fieldname
Format= "FreeFem" # FreeFem or VTK
Method="Greedy" #POD or Greedy
Rectification=1 #1 with Rectification post-process (Coarse Snapshots required) or 0 without

## Script Files - Initiate data
# Create data (mesh1,mesh2,snapshots,uH) for Sorbonne usecase 
""" 
--------------------------------------
              generate snapshots
--------------------------------------
"""
nbeOfInitSnapshots = 1

from NIRBinitCase import initproblem
print("-----------------------------------")
print(" STEP I. 0: start init             ")
print("-----------------------------------")
modelsFolder = osp.expanduser("~/devel/mordicus/src/poc-1/tests/Modules/Cemosis/DataCompressors/models/")
fineSnapList, coarseSnapList, CoarseMesh, FineMesh = initproblem(nbeOfInitSnapshots, modelsFolder=modelsFolder)
print("-----------------------------------")
print("STEP I.0 (bis): snapshots generated")
print("-----------------------------------")

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      Definition and initialisation of the problem
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

#print("number of modes: ",nev)

time=0.0
# ----------------------------------------------------------
# Get number of Snapshots and modes 
Nsfine = len(fineSnapList)
Nscoarse = len(coarseSnapList)

nev=1 #default value number of modes
if len(sys.argv)>1:
        nev=int(sys.argv[1]) 

# ----------------------------------------------------------
# Get coarse snapshots and coarse mesh if rectification processes
# if Rectification == 1:
        # coarseSnapListNp = []

        # for s in range(Nscoarse):
        #         fineSnapListNp.append(FeelppToNp(fineSnapList[s]))
        #         coarseSnapListNp.append(FeelppToNp(coarseSnapList[s]))
#         CoarseSnapshotsFile=glob.glob(os.path.join(CoarseDataFolder,"*.txt"))[0]
#         FFCoarsetoVTKconvert=FFSR.FFSolutionReader(FieldName,CoarseMeshFileName);
#         FFCoarsetoVTKconvert.FFReadToNp(externalFolder,CoarseSnapshotsFile) #create the snapshots with vtu format
# ----------------------------------------------------------

assert Nsfine>0, " !! no snapshots provided !! "
if len(sys.argv)>1:
        assert nev<=Nsfine, " !! To many number of modes, nev must be less than ns !!"
if Rectification == 1 and Nscoarse!=Nsfine:
        warnings.warn( "Not the same number of coarse and fine snapshots ->  not using the rectification post-process! ")
        Rectification = 0
# ----------------------------------------------------------
# ----------------------------------------------------------
## MESH READER
## Fine Mesh reader 
numberOfNodes = FineMesh.numGlobalPoints()
print("Fine Mesh --> Number of nodes : ", numberOfNodes)

## Coarse Mesh reader if rectification process 
if Rectification==1 :
        numberOfNodes2 = CoarseMesh.numGlobalPoints() 
        print("Coarse Mesh --> Number of nodes : ", numberOfNodes2)


# ----------------------------------------------------------
# # Interpolation on the fine mesh if rectification post-process
# if Rectification==1:
#         option="basictools" #ff, basictools
#         if Format == "FreeFem":
#                 Folder=str(Path(FineMeshFileName).parents[0])
#                 stem=str(Path(FineMeshFileName).stem)
#                 #print(stem[-4:])
#                 suffix=str(Path(FineMeshFileName).suffix)
#                 if stem[-4:]!="GMSH":
#                         FineMeshFileName =  Folder+"/"+stem+"GMSH"+suffix
#                 Folder=str(Path(CoarseMeshFileName).parents[0])
#                 stem=str(Path(CoarseMeshFileName).stem)
#                 suffix=str(Path(CoarseMeshFileName).suffix)
#                 if stem[-4:]!="GMSH":
#                         CoarseMeshFileName =  Folder+"/"+stem+"GMSH"+suffix
#         operator=IOW.InterpolationOperator(FineDataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)
#         #operator=SIO.LoadState(FineDataFolder+"/Matrices/operator")
# ----------------------------------------------------------
## READ SNAPSHOTS


# print("-----------------------------------")
# print(" STEP I. 1: reading snapshots      ")
# print("-----------------------------------")

# collectionProblemData = CPD.CollectionProblemData()
# collectionProblemData.AddVariabilityAxis('unused',int,description="unused parameter")
# collectionProblemData.DefineQuantity("U", full_name=FieldName, unit="unused") #fine
# if Rectification == 1:
#         collectionProblemData.DefineQuantity("UH", full_name=FieldName, unit="unused") #coarse

# parameters = range(Nsfine)#for problemdata

# cpt=0 #num snapshot

# ndof = numberOfNodes*nbeOfComponentsPrimal
# Fine_snapshot_array = np.zeros(ndof,)
# ## Reading fine snapshots
# for snap in fineSnapList :
#     print(f"Getting fine snapshot ", cpt)
#     for i in range(ndof):
#         Fine_snapshot_array[i] = snap.to_petsc().vec().__getitem__(i)
# #     Fine_snapshot_array= snap.to_petsc().vec().array  # get solution field  
#     solutionU=S.Solution("U",nbeOfComponentsPrimal,numberOfNodes,True) #Add each snapshot in collectionProblemData 
#     solutionU.AddSnapshot(Fine_snapshot_array,0) #time=0
#     problemData = PD.ProblemData(FineDataFolder+str(cpt)) #name of problemData
#     problemData.AddSolution(solutionU)
#     collectionProblemData.AddProblemData(problemData,unused=parameters[cpt])
#     cpt+=1

# cpt=0

# if Rectification == 1:
#         ndof = numberOfNodes2*nbeOfComponentsPrimal
#         Coarse_snapshot_array = np.zeros(ndof,)
#         ## Reading coarse snapshots
#         for snap in coarseSnapList :
#                 print(f"Getting coarse snapshot ", cpt)
#                 for i in range(ndof):
#                         Coarse_snapshot_array[i] = snap.to_petsc().vec().__getitem__(i)
#                 # Coarse_snapshot_array= snap.to_petsc().vec().array  # get solution field  
#                 solutionUH=S.Solution("U",nbeOfComponentsPrimal,numberOfNodes2,True) #Add each snapshot in collectionProblemData
#                 solutionUH.AddSnapshot(Coarse_snapshot_array,0) #time=0
#                 problemData = collectionProblemData.GetProblemData(unused=parameters[cpt]) #label of problemData=parameter[cpt]
#                 problemData.AddSolution(solutionUH)
#                 collectionProblemData.AddProblemData(problemData,unused=parameters[cpt])
#                 cpt+=1
                
# print("ComputeL2ScalarProducMatrix and ComputeH1ScalarProducMatrix ...")
# #l2ScalarProducMatrix = SIO.LoadState(FineDataFolder+"/Matrices/snapshotCorrelationOperator") #if already created
# #h1ScalarProducMatrix = SIO.LoadState(FineDataFolder+"/Matrices/h1ScalarProducMatrix")

# #from scipy import sparse
# #l2ScalarProducMatrix=sparse.eye(numberOfNodes*nbeOfComponentsPrimal) #works with identity matrix

# l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(FineMesh, nbeOfComponentsPrimal)
# h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(FineMesh, nbeOfComponentsPrimal)

# # Snapshots norm
# snapshotUIterator = collectionProblemData.SnapshotsIterator("U")
# snapshots = []
# #SnapshotsUNorm=[]
# for s in snapshotUIterator:
#     snapshots.append(s)
#     #norm=np.sqrt(s@l2ScalarProducMatrix@s)
#     #SnapshotsUNorm.append(norm)
#     #print("norm",norm)

# if Rectification==1:
#         snapshotUHIterator = collectionProblemData.SnapshotsIterator("UH")

#         snapshotsH = []
#         for s in snapshotUHIterator:
#                 snapshotsH.append(s)



# """
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
#                                       Greedy/POD  Offline part
# ----------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
# """

# print("-----------------------------------")
# print(" STEP I. 2: Creating Reduced Basis ")
# print("-----------------------------------")
# if Method=="Greedy":
#         reducedOrderBasisU=GD.Greedy(collectionProblemData,"U",l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorithm
# else: #POD 
#         reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-6, l2ScalarProducMatrix)

# print("number of modes: ", nev)
# ### Add basis to collectionProblemData
    
# collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
# collectionProblemData.CompressSolutions("U", l2ScalarProducMatrix) #Mass matrix
# nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")

# collectionProblemData.AddOperatorCompressionData("U", l2ScalarProducMatrix)
# collectionProblemData.AddDataCompressionData("U", h1ScalarProducMatrix)

# ## Ortho basis verification
# """
# for i in range(nev):
#     for j in range(nev):
#         t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
#         norm=t.dot(reducedOrderBasisU[j,:])
#         normh1=reducedOrderBasisU[i,:]@(h1ScalarProducMatrix@reducedOrderBasisU[j,:])
#         print(i,j," ",norm)
#         print(" normh1 ", normh1)
# """
        
# ### PT: Rectification
# print("----------------------------------------")
# print(" STEP I. 3. : Rectification PostProcess ")
# print("----------------------------------------")
# # determinist process: Matrix R, allows to go from coeff (uH,phi_i) to (uh,Phi_i)
# if Rectification == 1:
#         GD.addRectificationTocollectionProblemData(collectionProblemData,"U","UH",l2ScalarProducMatrix,nev) # greedy algorithm
        

# ### Offline Errors
# print("-----------------------------------")
# print(" STEP I. 4: Offline  errors        ")
# print("-----------------------------------")

# L2compressionErrors=[]
# H1compressionErrors=[]

# for _, problemData in collectionProblemData.GetProblemDatas().items(): #for each snapshot
#     solutionU=problemData.GetSolution("U")
#     CompressedSolutionU=solutionU.GetCompressedSnapshots()
#     exactSolution = problemData.solutions["U"].GetSnapshot(0)
#     reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    
#     norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
#     normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))
   
#     if norml2ExactSolution !=0 and normh1ExactSolution != 0:
#         err=reconstructedCompressedSolution-exactSolution
#         relL2Error=np.sqrt(err@l2ScalarProducMatrix@err)/norml2ExactSolution
#         relH1Error=np.sqrt(err@h1ScalarProducMatrix@err)/normh1ExactSolution
    
#     else: #erreur absolue
#         relL2Error=np.sqrt(err@l2ScalarProducMatrix@err)
#         relH1Error=np.sqrt(err@h1ScalarProducMatrix@err)
        
#     L2compressionErrors.append(relL2Error)
#     H1compressionErrors.append(relH1Error)
    
# print("compression relative errors L2 =", L2compressionErrors)
# print("compression relative errors H1 =", H1compressionErrors)

# print("Offline DONE ... ")
# print("to be continued, with the online part ... ")

# ## save results
# print("Save state in ",OfflineResuFolder)
# # collectionProblemData.SetDataCompressionData("h1ScalarProducMatrix",h1ScalarProducMatrix)
# # collectionProblemData.SetOperatorCompressionData(l2ScalarProducMatrix)
# FileName=OfflineResuFolder+"collectionProblemData"
# SIO.SaveState(FileName, collectionProblemData)
# # SIO.SaveState("h1ScalarProducMatrix", h1ScalarProducMatrix)
# # SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)

