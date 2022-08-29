# -*- coding: utf-8 -*-
## NIRB script python Online part 
## Elise Grosjean
## 01/2021

from dataclasses import Field
# from fileinput import filename
from hashlib import new
import os
import os.path as osp
import glob
from sqlite3 import DatabaseError
import sys
from turtle import shape
import numpy as np
from pathlib import Path
import array
import warnings
import timeit 


import feelpp 
import feelpp.mor as mor 
import feelpp.mor.reducedbasis.reducedbasis as FppRb
import feelpp.operators as FppOp 
import SnapshotReducedBasis as SRB
from Mordicus.Modules.Cemosis.Containers.SolutionStructure.FeelppSol import FeelppSolution as FppSol
from NIRBinitCase import * 
from Mordicus.Modules.Cemosis.IO.StateIO import *


print("-----------------------------------")
print(" STEP II. 0: start Online nirb     ")
print("-----------------------------------")


#time=0.0 #steady
## Directories
currentFolder=os.getcwd()
dataFolder = osp.expanduser("~/feelppdb/nirb/")
dataFolder = osp.expanduser("~/feelppdb/nirb/heat/np_1/")
modelFolder = "heat" # or "heat"


## Parameters

dimension=2 #dimension spatial domain
nbeOfComponentsPrimal = 2 # number of components 
FieldName="Velocity" #Snapshots fieldname
FieldNameExactSolution="u"#"Velocity" #Snapshots fieldname
Format= "FreeFem" # FreeFem or VTK
Method="POD" #POD or Greedy
Rectification=0 #1 with Rectification post-process (Coarse Snapshots required) or 0 without
ComputingError=1 # 1 if the fine solution is provided 
SavingApproximation=1 #if NIRB approximation saved

## Fine and coarse Solution files name
#coarseName="snapshotH0.vtu"
#fineName="snapshot0.vtu"

""" 
--------------------------------------
        initialize toolbox 
--------------------------------------
"""
## Current Directories
currentFolder=os.getcwd()

# model directories 
toolboxesOptions='heat'

modelsFolder = f"{currentFolder}/models/" 
modelsFolder = f"{modelsFolder}{toolboxesOptions}" 
cfg_path = f"{modelsFolder}/square/square.cfg" 
geo_path = f"{modelsFolder}/square/square.geo"
model_path = f"{modelsFolder}/square/square.json"

msh_path = f"{dataFolder}/square.msh"

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

tbCoarse = setToolbox(H, geo_path, model, order)
tbFine = setToolbox(h, geo_path, model,order)
Dmu = loadParameterSpace(model_path)

# ----------------------------------------------------------
# ----------------------------------------------------------
## MESH infos 
FineMesh = tbFine.mesh()
CoarseMesh = tbCoarse.mesh()
numberOfNodes = CoarseMesh.numGlobalPoints()

""" 
-------------------------------------------------------
         Load offline datas for online part 
-------------------------------------------------------
"""
filename= dataFolder + "reducedBasisU.dat"
reducedOrderBasisU = LoadPetscArrayBin(filename)
nev = reducedOrderBasisU.size[0]
filename= dataFolder + "massMatrix.dat"
MassMatrix = LoadPetscArrayBin(filename)
filename= dataFolder + "stiffnessMatrix.dat"
StiffnessMatrix = LoadPetscArrayBin(filename)

MassMatrix.assemble()
StiffnessMatrix.assemble()

l2ScalarProducMatrix = MassMatrix
h1ScalarProducMatrix = StiffnessMatrix
""" 
-----------------------------------------------------------------
        Get coarse solution and project it on fine mesh 
-----------------------------------------------------------------
"""
## Solve equation with new parameter on Coarse Mesh
mu = Dmu.element()
coarseSol = SolveFpp(tbCoarse, mu)
interpOper = createInterpolator(tbCoarse, tbFine)
interpSol = interpOper.interpolate(coarseSol)

""" 
-------------------------------------------------------
         Get new solution on fine mesh 
-------------------------------------------------------
"""
## Compute coeff on reduced basis 
newSol = FppSol("UH",dimension, numberOfNodes) 
newSol.AddSolution(interpSol, 0)
newSol.CompressSolution(l2ScalarProducMatrix, reducedOrderBasisU)
newCompressedSol = newSol.GetCompressedSolution()

## Get new reconstructed solution  
reconstructedSolution = interpSol.to_petsc().vec().copy()
reducedOrderBasisU.multTranspose(newCompressedSol[0], reconstructedSolution)

##################################################
# Save Online data for vizualisation 
##################################################

print("-----------------------------------")
print(" STEP II. 4: Saving datas on Disk  ")
print("-----------------------------------")

# export = feelpp.exporter(mesh=FineMesh, name="feelpp_nirb")
# export.addScalar("un", 1.)
# export.addP1c("u", reconstructedSolution)
# export.addP1c("U_interp", interpSol)
# e.addP0d("pid", feelpp.pid(P0h))
# export.save()
##################################################
# ONLINE ERRORS
##################################################
if ComputingError==1:

        print("-----------------------------------")
        print(" STEP II. 3: Compute online errors ")
        print("-----------------------------------")

        FineSol = SolveFpp(tbFine, mu)

        diffSolve = FineSol.to_petsc().vec() - reconstructedSolution 
        diffInterp = FineSol.to_petsc().vec() - interpSol.to_petsc().vec() 
        
        print("---------- NIRB Solve Error -----------------")
        print ('l2-norm  =', diffSolve.norm())
        print ('Infinity-norm =', diffSolve.norm(PETSc.NormType.NORM_INFINITY))

        print("---------- NIRB Interp Error -----------------")
        print ('l2-norm  =', diffInterp.norm())
        print ('Infinity-norm =', diffInterp.norm(PETSc.NormType.NORM_INFINITY))

        print("-----------------------------------------------")

print("NIRB ONLINE DONE! ")



