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

from Mordicus.Modules.Cemosis.Containers.SolutionStructure.FeelppSol import energy
from NIRBinitCase import * 
from feelpp.toolboxes.heat import toolboxes_options 
from Mordicus.Modules.Cemosis.IO.StateIO import *
from feelpp.mor.nirb.nirb import *

print("-----------------------------------")
print(" STEP II. 0: start Online nirb     ")
print("-----------------------------------")

## Parameters
dimension=2 #dimension spatial domain
Method="POD" #POD or Greedy
Rectification=0 #1 with Rectification post-process (Coarse Snapshots required) or 0 without
ComputingError=True # 1 will take more time for compution direct FE solution in fine mesh 
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
tbCoarse = setToolbox(H, geo_path, model, dim=dimension, order=order,type_tb=toolboxesOptions)
tbFine = setToolbox(h, geo_path, model, dim=dimension, order=order,type_tb=toolboxesOptions)
# Get actual mu parameter 
Dmu = loadParameterSpace(model_path) 

# ----------------------------------------------------------
# ----------------------------------------------------------
## MESH infos 
FineMesh = tbFine.mesh()
CoarseMesh = tbCoarse.mesh()
numberOfNodes = CoarseMesh.numGlobalPoints()
# Define feelpp function space  
Xh = feelpp.functionSpace(mesh=FineMesh, order=order)

""" 
-------------------------------------------------------
         Load offline datas for online part 
-------------------------------------------------------
"""
filename= dataFolder + "reducedBasisU.dat"
reducedOrderBasisU = LoadPetscArrayBin(filename)
nev = reducedOrderBasisU.size[0]
filename= dataFolder + "massMatrix.dat"
l2ScalarProducMatrix = LoadPetscArrayBin(filename)
filename= dataFolder + "stiffnessMatrix.dat"
h1ScalarProducMatrix = LoadPetscArrayBin(filename)
l2ScalarProducMatrix.assemble()
h1ScalarProducMatrix.assemble()
""" 
-----------------------------------------------------------------
        Get coarse solution and project it on fine mesh 
-----------------------------------------------------------------
"""
## Solve equation with new parameter on Coarse Mesh
mu = Dmu.element()
coarseSol = SolveFpp(tbCoarse, mu)
interpOper = createInterpolator(tbCoarse, tbFine, type_tb=toolboxesOptions)
interpSol = interpOper.interpolate(coarseSol)

# Export interpolated sol
if export :
        ep = feelpp.exporter(mesh=FineMesh, name="feelpp_interp")
        ep.addScalar("un", 1.) 
        if (order==1):
                ep.addP1c("U_interp", interpSol)
        elif (order==2):
                ep.addP2c("U_interp", interpSol)
        ep.save()

""" 
-------------------------------------------------------
         Get new solution on fine mesh 
-------------------------------------------------------
"""
## Get projection of interpolate solution on reduced space 
newSol = FppSol("UH",dimension, numberOfNodes) 
newSol.AddSolution(interpSol, 0)
newSol.CompressSolution(l2ScalarProducMatrix, reducedOrderBasisU)
newCompressedSol = newSol.GetCompressedSolution()

## Get new reconstructed solution in PETSc format 
resPETSc = Xh.element().to_petsc()
reducedOrderBasisU.multTranspose(newCompressedSol[0], resPETSc.vec())

##################################################
# Save Online data for vizualisation 
##################################################
print("-----------------------------------")
print(" STEP II. 4: Saving datas on Disk  ")
print("-----------------------------------")
resFpp = Xh.element(resPETSc) # convert to feelpp element function 
# Export NIRB approximation sol
if export :
        ep = feelpp.exporter(mesh=FineMesh, name="feelpp_nirb_discr")
        ep.addScalar("un", 1.) 
        if (order==1):
                ep.addP1c("U_nirb", resFpp)
        elif (order==2):
                ep.addP2c("U_nirb", resFpp)
        ep.save()

##################################################
# ONLINE ERRORS
##################################################

if ComputingError :

        print("-----------------------------------")
        print(" STEP II. 3: Compute online errors ")
        print("-----------------------------------")

        FineSol = SolveFpp(tbFine, mu) # Get the FE solution calculate directly in the fine mesh  


        # Export interpolated sol
        if export :
                ep = feelpp.exporter(mesh=FineMesh, name="feelpp_finesol")
                ep.addScalar("un", 1.) 
                if (order==1):
                        ep.addP1c("U_fine", FineSol)
                elif (order==2):
                        ep.addP2c("U_fine", FineSol)
                ep.save()

        diffSolve = FineSol.to_petsc().vec() - resPETSc.vec() 
        diffInterp = (FineSol - interpSol).to_petsc().vec() 
        
        error = []
        error.append(nev)
        error.append(diffSolve.norm())
        error.append(diffSolve.norm(PETSc.NormType.NORM_INFINITY))

        # error = np.array(error)
        filename = 'nirb_error.txt'
        WriteVecAppend(filename, error)
        # np.savetxt(filename, error)

        print("---------- NIRB Solve absolute Error -----------------")
        print ('l2-norm  =', error[1])
        print ('Infinity-norm =', error[2])

        print("---------- NIRB Solve relative Error -----------------")
        print ('l2-norm  =', error[1]/FineSol.to_petsc().vec().norm())
        print ('Infinity-norm =', error[2]/FineSol.to_petsc().vec().norm(PETSc.NormType.NORM_INFINITY))

        print("---------- NIRB Interp Error -----------------")
        print ('l2-norm  =', diffInterp.norm())
        print ('Infinity-norm =', diffInterp.norm(PETSc.NormType.NORM_INFINITY))

        print("-----------------------------------------------")


finish = timeit.timeit() 
print("Elapsed time = ", finish - start )
print("NIRB ONLINE DONE ! ")



