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
from petsc4py import PETSc
from feelpp.mor.nirb.nirb import * 

# from Mordicus.Core.Containers import CollectionProblemData as CPD
# from Mordicus.Core.IO import StateIO as SIO


print("-----------------------------------")
print(" STEP II. 0: start Online nirb     ")
print("-----------------------------------")

## Parameters
dimension=2 #dimension spatial domain
Method="POD" #POD or Greedy
Rectification=True #True with Rectification post-process (Coarse Snapshots required) or 0 without
ComputingError=True # True will take more time for compution direct FE solution in fine mesh 
export = True # True will save the NIRB result and interpolation of coarse solution in fine mesh  
toolboxesOptions='heat'
modelfile={'heat':'square/square', 'fluid':'lid-driven-cavity/cfd2d'}
order = 1
# fineness of two grids
H = 0.1  # CoarseMeshSize 
h = H**2 # fine mesh size 


## Directories
PWD=os.getcwd()
dataFolder = osp.expanduser(f"~/feelppdb/nirb/{toolboxesOptions}/np_1/")
# model directories 
modelsFolder = f"{PWD}/models/" 
modelsFolder = f"{modelsFolder}{toolboxesOptions}/" 
cfg_path = f"{modelsFolder}{modelfile[toolboxesOptions]}.cfg" 
geo_path = f"{modelsFolder}{modelfile[toolboxesOptions]}.geo"
model_path = f"{modelsFolder}{modelfile[toolboxesOptions]}.json"
msh_path = f"{dataFolder}{modelfile[toolboxesOptions]}.msh"

""" 
--------------------------------------
        initialize toolbox 
--------------------------------------
"""
start = timeit.timeit()
# set the feelpp environment
config = feelpp.globalRepository(f"nirb/{toolboxesOptions}")
e=feelpp.Environment(sys.argv, opts = toolboxes_options(toolboxesOptions).add(mor.makeToolboxMorOptions()), config=config)
e.setConfigFile(cfg_path)

# load model 
model = loadModel(model_path)
# define the toolboxes 
tbFine = setToolbox(h, geo_path, model, dim=dimension, order=order,type_tb=toolboxesOptions)
# Get actual mu parameter 
Dmu = loadParameterSpace(model_path) 

# ----------------------------------------------------------
# ----------------------------------------------------------
## Fine mesh infos 
FineMesh = tbFine.mesh()
numberOfNodes = FineMesh.numGlobalPoints()
print("Fine Mesh --> Number of nodes : ", numberOfNodes)

if Rectification :
        # define the coarse toolboxes and mesh 
        tbCoarse = setToolbox(H, geo_path, model, dim=dimension, order=order,type_tb=toolboxesOptions)
        CoarseMesh = tbCoarse.mesh()
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
if Rectification :
        fineSnapList, coarseSnapList = initproblem(nbeOfInitSnapshots, Dmu, tbFine, tbCoarse, type_tb=toolboxesOptions)
else :
        fineSnapList, _ = initproblem(nbeOfInitSnapshots,Dmu, tbFine, type_tb=toolboxesOptions)

"""
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      Greedy/POD  Offline part
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
"""
print("--------------------------------------------")
print(" STEP I. 2: Generate L2 and H1 operator     ")
print("--------------------------------------------")

Vh = feelpp.functionSpace(mesh=FineMesh) # feelpp space function 
l2ScalarProducMatrix=FppOp.mass(test=Vh,trial=Vh,range=feelpp.elements(FineMesh))
h1ScalarProducMatrix=FppOp.stiffness(test=Vh,trial=Vh,range=feelpp.elements(FineMesh))

print("-----------------------------------")
print(" STEP I. 2: Creating Reduced Basis ")
print("-----------------------------------")    
# collectionProblemData = CPD.CollectionProblemData()
# collectionProblemData.AddVariabilityAxis('unused',int,description="unused parameter")
# collectionProblemData.DefineQuantity("U", full_name=FieldName, unit="unused") #fine
# if Rectification == 1:
#         collectionProblemData.DefineQuantity("UH", full_name=FieldName, unit="unused") #coarse

cpt=0 #num snapshot        
if Method=="Greedy":
        #reducedOrderBasisU=GD.Greedy(collectionProblemData,"U",l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorith
        reducedOrderBasisU = SRB.PODReducedBasisPETSc(fineSnapList,l2ScalarProducMatrix)
else : #POD 
        # reducedOrderBasisU = SRB.PODReducedBasisPETSc(fineSnapList, l2ScalarProducMatrix)
        reducedOrderBasisU = SRB.PODReducedBasisNumpy(fineSnapList, l2ScalarProducMatrix)

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
