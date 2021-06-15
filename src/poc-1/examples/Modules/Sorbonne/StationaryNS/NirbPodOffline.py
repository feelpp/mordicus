# -*- coding: utf-8 -*-
## NIRB script python Offline part (with VTK)
## Elise Grosjean
## 01/2021

import os
import os.path as osp

import subprocess
import sys
#from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Modules.sorbonne.IO import MeshReader as MR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.sorbonne.IO import VTKSolutionReader as VTKSR
from Mordicus.Modules.sorbonne.IO import FFSolutionReader as FFSR
from Mordicus.Modules.sorbonne.IO import numpyToVTKWriter as NpVTK
from Mordicus.Modules.sorbonne.IO import InterpolationOperatorWriter as IOW
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Modules.sorbonne.MOR import Greedy as GD
#from tkinter.constants import CURRENT
from initCase import initproblem
import glob
import numpy as np
from pathlib import Path
import array

#from Mordicus.Modules.sorbonne.IO.FFSolutionReader import FFSolutionReader

"""
Create data (mesh1,mesh2,snapshots,uH) for Sorbonne usecase
"""
"""
----------------------------
              generate snapshots
----------------------------
"""

## Directories
currentFolder=os.getcwd()
dataFolder=osp.join(currentFolder,'StationaryNSData')


## Script Files - Initiate data
externalFolder=osp.join(currentFolder,'External')


print("-----------------------------------")
print(" STEP0: start init                 ")
print("-----------------------------------")
#initproblem(dataFolder)
print("-----------------------------------")
print(" STEP0: snapshots generated        ")
print("-----------------------------------")

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      Definition and initialisation of the problem
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

nev=1   #number of modes
if len(sys.argv)>1:
        nev=int(sys.argv[1])
print("number of modes: ",nev)

time=0.0
dimension=2
FieldName="u"

FineSnapshotFiles=sorted(glob.glob(dataFolder+"/snapshots_*"))
ns=len(FineSnapshotFiles)
print("number of snapshots: ",ns)

#CoarseSnapshotFiles=sorted(glob.glob(dataFolder+"/coarsesnapshots_*"))
#assert(len(CoarseSnapshotFiles) == ns), "not the same number of fine/coarse snapshots!"

## FINE MESH reader (vtu file)
FineMeshFileName=FineSnapshotFiles[0]
meshReader = MR.MeshReader(FineMeshFileName,dimension)
fineMesh = meshReader.ReadMesh()
print("Fine mesh defined in " + FineMeshFileName + " has been read")

nbeOfComponentsPrimal = 2
numberOfNodes = fineMesh.GetNumberOfNodes()
print("number of nodes for the fineMesh: ",numberOfNodes)

## COARSE MESH
"""
CoarseMeshFileName=CoarseSnapshotFiles[0]
meshReader = MR.MeshReader(CoarseMeshFileName,dimension)
coarseMesh = meshReader.ReadMesh()
print("Coarse mesh defined in " + CoarseMeshFileName + " has been read")


## interpolation
option="basictools" #ff, basictools 
operator=IOW.InterpolationOperator(dataFolder,FineMeshFileName,CoarseMeshFileName,dimension,option=option)
"""

collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('unused',int,description=" variability")
collectionProblemData.defineQuantity("U", full_name=FieldName, unit="m/s")
#collectionProblemData.defineQuantity("UH", full_name=FieldName, unit="m/s")
parameters=range(ns) #for problemdata

suffix=str(Path(FineSnapshotFiles[0]).suffix)
cpt=0 #num snapshot
#### Read solutions 
for i in range(ns):
    VTKSnapshotReader=VTKSR.VTKSolutionReader(FieldName)
    SnapshotFile=dataFolder+"/"+str(Path(FineSnapshotFiles[i]).stem)+suffix
    print(SnapshotFile)
    FineSnapshot=VTKSnapshotReader.VTKReadToNp(SnapshotFile).flatten()

    solutionU=S.Solution("U",dimension,numberOfNodes,True)
    ### Only one snapshot --> time 0
    solutionU.AddSnapshot(FineSnapshot,0)

    problemData = PD.ProblemData(dataFolder+str(i))
    problemData.AddSolution(solutionU)
    collectionProblemData.AddProblemData(problemData,unused=parameters[i])

snapshotsIterator = collectionProblemData.SnapshotsIterator("U")
snapshots = []
for s in snapshotsIterator:
    snapshots.append(s)
#print(np.shape(snapshots))


#numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)

""" POD """
print("-----------------------------------")
print(" STEP1: POD Offline                ")
print("-----------------------------------")

print("ComputeL2ScalarProducMatrix ...")

l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(fineMesh, nbeOfComponentsPrimal)
h1ScalarProducMatrix = FT.ComputeH10ScalarProductMatrix(fineMesh, nbeOfComponentsPrimal)
"""for s in snapshotsIterator:
    snapshots.append(s)
    t=l2ScalarProducMatrix.dot(s)
    norm=t.dot(s)
    print("norm",np.sqrt(norm))
print("snap",np.shape(snapshots))"""

#test=NpVTK.VTKWriter(VTKBase);

reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-6, l2ScalarProducMatrix)

collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)

collectionProblemData.CompressSolutions("U", l2ScalarProducMatrix)

#base orthonorme?
"""
for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        print(i,j," ",norm)
"""

### Offline Errors
print("-----------------------------------")
print(" STEP I. 4: Offline  errors        ")
print("-----------------------------------")

L2compressionErrors=[]
H1compressionErrors=[]

#Offline errors

for _, problemData in collectionProblemData.GetProblemDatas().items(): #for each snapshot
    solutionU=problemData.GetSolution("U")
    CompressedSolutionU=solutionU.GetCompressedSnapshots()
    exactSolution = problemData.solutions["U"].GetSnapshot(0)
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0
    
    norml2ExactSolution=np.sqrt(exactSolution@(l2ScalarProducMatrix@exactSolution))
    normh1ExactSolution=np.sqrt(exactSolution@(h1ScalarProducMatrix@exactSolution))
    
    if norml2ExactSolution !=0 and normh1ExactSolution != 0:
        err=reconstructedCompressedSolution-exactSolution
        relL2Error=np.sqrt(err@l2ScalarProducMatrix@err)/norml2ExactSolution
        relH1Error=np.sqrt(err@h1ScalarProducMatrix@err)/normh1ExactSolution
    
    else: #erreur absolue
        relL2Error=np.sqrt(err@l2ScalarProducMatrix@err)
        relH1Error=np.sqrt(err@h1ScalarProducMatrix@err)
        
    L2compressionErrors.append(relL2Error)
    H1compressionErrors.append(relH1Error)
    
print("compression relative errors L2 =", L2compressionErrors)
print("compression relative errors H1 =", H1compressionErrors)

print("Offline DONE ... ")
print("to be continued, with the online part ... ")

## save results
print("Save state in ", currentFolder+"/collectionProblemData")

collectionProblemData.SetOperatorCompressionData(l2ScalarProducMatrix)
SIO.SaveState(dataFolder+"/collectionProblemData", collectionProblemData)
#SIO.SaveState("h1ScalarProducMatrix", h1ScalarProducMatrix)
#SIO.SaveState("snapshotCorrelationOperator", l2ScalarProducMatrix)

