# -*- coding: utf-8 -*-
## NIRB script python Offline part 
## Elise Grosjean
## 01/2021

from ast import MatMult
from email import parser
from fileinput import filename
import os
import os.path as osp
import glob
import sys
import timeit
import numpy as np
from pathlib import Path
import array
import warnings
import feelpp 

import feelpp.mor as mor 
import feelpp.mor.reducedbasis.reducedbasis as FppRb
import feelpp.operators as FppOp 
import SnapshotReducedBasis as SRB 
from NIRBinitCase import * 
from feelpp.toolboxes.heat import *
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from petsc4py import PETSc

nirb_dir = "/data/home/elarif/devel/feelpp/python/pyfeelpp-toolboxes/feelpp/toolboxes/nirb/"
sys.path.append(nirb_dir)
from nirb import *

from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.IO import StateIO as SIO


## Directories
currentFolder=os.getcwd()
dataFolder = osp.expanduser("~/feelppdb/nirb/")
modelFolder = "StationaryNS/" # or "heat"

## Parameters

dimension=2 #dimension spatial domain
nbeOfComponentsPrimal = 2 # number of components 
FieldName="Velocity" #Snapshots fieldname
Method="POD" #POD or Greedy
Rectification=1 #1 with Rectification post-process (Coarse Snapshots required) or 0 without

## Script Files - Initiate data
# Create data (mesh1,mesh2,snapshots,uH) for Sorbonne usecase 
""" 
--------------------------------------
        initialize toolbox 
--------------------------------------
"""
## Current Directories
currentFolder=os.getcwd()

# model directories 
toolboxesOptions='heat' # 'fluid'

if (toolboxesOptions=='heat') :
        modelsFolder = f"{currentFolder}/models/" 
        modelsFolder = f"{modelsFolder}{toolboxesOptions}" 
        cfg_path = f"{modelsFolder}/square/square.cfg" 
        geo_path = f"{modelsFolder}/square/square.geo"
        model_path = f"{modelsFolder}/square/square.json"
elif (toolboxesOptions=='fluid'):
        modelsFolder = f"{currentFolder}/models/lid-driven-cavity" 
        # modelsFolder = f"{modelsFolder}{toolboxesOptions}" 
        cfg_path = f"{modelsFolder}/cfd2d.cfg" 
        geo_path = f"{modelsFolder}/cfd2d.geo"
        model_path = f"{modelsFolder}/cfd2d.json"


start = timeit.timeit() 

# fineness of two grids
H = 0.1  # CoarseMeshSize 
h = H**2 # fine mesh size 

# set the feelpp environment
config = feelpp.globalRepository(f"nirb/{toolboxesOptions}")
e=feelpp.Environment(sys.argv, opts = toolboxes_options(toolboxesOptions).add(mor.makeToolboxMorOptions()), config=config)
e.setConfigFile(cfg_path)
order =1

# load model 
model = loadModel(model_path)

tbCoarse = setToolbox(H, geo_path, model, dim=dimension, order=order,type_tb=toolboxesOptions)
tbFine = setToolbox(h, geo_path, model, dim=dimension, order=order,type_tb=toolboxesOptions)
Dmu = loadParameterSpace(model_path)
# ----------------------------------------------------------
# ----------------------------------------------------------
## MESH infos 
FineMesh = tbFine.mesh()
CoarseMesh = tbCoarse.mesh()
## Fine Mesh reader 
numberOfNodes = FineMesh.numGlobalPoints()
print("Fine Mesh --> Number of nodes : ", numberOfNodes)

## Coarse Mesh reader if rectification process 
if Rectification==1 :
        numberOfNodes2 = CoarseMesh.numGlobalPoints() 
        print("Coarse Mesh --> Number of nodes : ", numberOfNodes2)

""" 
--------------------------------------
              generate snapshots
--------------------------------------
"""
nbeOfInitSnapshots = 10
nev =nbeOfInitSnapshots 
print("-----------------------------------")
print(" STEP I. 0: start init             ")
print("-----------------------------------")

fineSnapList, coarseSnapList = initproblem(nbeOfInitSnapshots, tbFine, tbCoarse, Dmu)

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      Greedy/POD  Offline part
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""

print("-----------------------------------")
print(" STEP I. 2: Generate operator      ")
print("-----------------------------------")

Vh = feelpp.functionSpace(mesh=FineMesh)
MassMatrix=FppOp.mass(test=Vh,trial=Vh,range=feelpp.elements(FineMesh))
StiffnessMatrix=FppOp.stiffness(test=Vh,trial=Vh,range=feelpp.elements(FineMesh))

l2ScalarProducMatrix = MassMatrix
h1ScalarProducMatrix = StiffnessMatrix

print("-----------------------------------")
print(" STEP I. 2: Creating Reduced Basis ")
print("-----------------------------------")
        
collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.AddVariabilityAxis('unused',int,description="unused parameter")
collectionProblemData.DefineQuantity("U", full_name=FieldName, unit="unused") #fine
if Rectification == 1:
        collectionProblemData.DefineQuantity("UH", full_name=FieldName, unit="unused") #coarse

cpt=0 #num snapshot

nbPODMode = len(fineSnapList)
nbDofs = fineSnapList[0].functionSpace().nDof() 

oper = l2ScalarProducMatrix.mat()
oper.assemble()
oper = np.array(oper[:,:])
snaparray = []
for s in fineSnapList:
        snaparray.append(s.to_petsc().vec()[:])
        
if Method=="Greedy":
        #reducedOrderBasisU=GD.Greedy(collectionProblemData,"U",l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorith
        reducedOrderBasisU = SRB.ComputeReducedOrderBasisWithPOD(fineSnapList,l2ScalarProducMatrix)
else : #POD 
        # reducedOrderBasisU = SRB.ComputeReducedOrderBasisWithPOD(fineSnapList, l2ScalarProducMatrix)
        rbb = SP.ComputeReducedOrderBasis(snaparray, oper, 1.e-6)

nbPODMode = rbb.shape[0]
reducedOrderBasisU = PETSc.Mat().createDense(size=(nbPODMode,nbDofs))
reducedOrderBasisU.setFromOptions()
reducedOrderBasisU.setUp()
reducedOrderBasisU.assemble()

print('shape = ', rbb.shape)
reducedOrderBasisU[:,:] = rbb
# number of modes 
nev = reducedOrderBasisU.size[0]
print("number of modes: ", nev)

### Add basis to collectionProblemData
# collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
# # collectionProblemData.CompressSolutions("U", l2ScalarProducMatrix) #Mass matrix
# nev=collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
# collectionProblemData.AddOperatorCompressionData("U", l2ScalarProducMatrix) # Mass matrix 
# collectionProblemData.AddDataCompressionData("U", h1ScalarProducMatrix) # Energy matrix 


print("----------------------------------------")
print(" STEP I. 3: Save datas for Online phase ")
print("----------------------------------------")


from Mordicus.Modules.Cemosis.IO.StateIO import *
file = "massMatrix.dat"
SavePetscArrayBin(file, l2ScalarProducMatrix.mat())
file = "stiffnessMatrix.dat"
SavePetscArrayBin(file, h1ScalarProducMatrix.mat())
file="reducedBasisU.dat"
SavePetscArrayBin(file, reducedOrderBasisU)
# SIO.SaveState(file, reducedOrderBasisU)

## Ortho basis verification
"""
for i in range(nev):
    for j in range(nev):
        t=l2ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
        norm=t.dot(reducedOrderBasisU[j,:])
        normh1=reducedOrderBasisU[i,:]@(h1ScalarProducMatrix@reducedOrderBasisU[j,:])
        print(i,j," ",norm)
        print(" normh1 ", normh1)
"""

### Offline Errors
# print("-----------------------------------")
# print(" STEP I. 4: Offline  errors soon !!")
# print("-----------------------------------")

finish = timeit.timeit() 
print("Elapsed time = ", finish - start )
print("Offline DONE ... ")
print("to be continued, with the online part ... ")
