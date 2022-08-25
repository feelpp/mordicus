# -*- coding: utf-8 -*-
## NIRB script python Online part 
## Elise Grosjean
## 01/2021

from dataclasses import Field
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


import feelpp 
import feelpp.mor as mor 
import feelpp.mor.reducedbasis.reducedbasis as FppRb
import feelpp.operators as FppOp 
import SnapshotReducedBasis as SRB
from Mordicus.Modules.Cemosis.Containers.SolutionStructure.FeelppSol import FeelppSolution as FppSol
from NIRBinitCase import * 
from Mordicus.Core.IO import StateIO as SIO


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

reducedOrderBasisU = SIO.LoadState(dataFolder+"reducedBasisU")
nev = reducedOrderBasisU.shape[0]

# to be done later (read the matrix from file)
Vh = feelpp.functionSpace(mesh=FineMesh)
MassMatrix=FppOp.mass(test=Vh,trial=Vh,range=feelpp.elements(FineMesh))
StiffnessMatrix=FppOp.stiffness(test=Vh,trial=Vh,range=feelpp.elements(FineMesh))
MassMatrix.mat().assemble()
StiffnessMatrix.mat().assemble()

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
newCompressedSol = newSol.GetreducedCoeff()
reconstructedSolution = np.dot(newCompressedSol[0], reducedOrderBasisU)


##################################################
# ONLINE ERRORS
##################################################
if ComputingError==1:
    
    print("-----------------------------------")
    print(" STEP II. 3: Compute online errors ")
    print("-----------------------------------")

    fineSol = np.array(interpSol.to_petsc().vec())
    reducedSol = reconstructedSolution 
    diff = np.abs(fineSol - reducedSol)

    print('Inf norm = ', np.max(diff)/np.max(fineSol))
    print('l2 discret norm = ',np.sqrt(diff.dot(diff))/np.sqrt(fineSol.dot(fineSol)) )

print("NIRB ONLINE DONE! ")



