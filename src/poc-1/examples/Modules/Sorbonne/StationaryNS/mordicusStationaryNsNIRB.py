import os
import os.path as osp

import subprocess
from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
#from tkinter.constants import CURRENT
#from Mordicus.Modules.sorbonne.IO import FFSolutionReader
from initCase import initproblem
from initCase import basisFileToArray
from initCase import VTKReadToNp

import array

#from Mordicus.Modules.sorbonne.IO.FFSolutionReader import FFSolutionReader

"""
Create data (mesh1,mesh2,snapshots,uH) for Sorbonne     usecase
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
dataFolder=osp.join(currentFolder,'StationaryNSData')
initproblem(dataFolder)
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
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
nev=3                           
time=0.0 
dimension=2
# dim
           
# instancie a reader solution           
collectionProblemData = CPD.CollectionProblemData()
for i in range(nev):
    
    u1_np_array = VTKReadToNp(dataFolder+"/snapshot",i)
    #instancie une solution
    solutionU=S.Solution("U",dimension,u1_np_array.shape[0],True)
    u1_np_array=u1_np_array.flatten()
        
    ### ajouter la snapshot A solutionU
    
    solutionU.AddSnapshot(u1_np_array,time)
    problemData = PD.ProblemData(dataFolder)
    problemData.AddSolution(solutionU)

collectionProblemData.AddProblemData(problemData)

##On lit le maillage ici si GMSH et convertir en format gmsh sinon pour le lire avec basictools
meshFileName = dataFolder + "/test.msh"

meshReader = GMR.GmshMeshReader(meshFileName)
mesh = meshReader.ReadMesh()
print("Mesh defined in " + meshFileName + " has been read")



""" 
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
    OFFLINE Ici on choisi
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
""" 


"""        
----------------------------
              generate basis
----------------------------
""" 


#print(tmpbase)

# The following should be executed with python > 3.5

"""Script FreeFem
"""
scriptFreeFem=osp.join(externalFolder,'NIRB_GREEDY_OFFLINE.edp')

"""Input
"""
meshFile1 = osp.join(dataFolder,'mesh1.msh')
snapshotsFile = osp.join(dataFolder,"snapshots.txt")


"""Output
"""
tmpbaseFile=osp.join(dataFolder,"RBasis")    # reduced basis resulting from the offline stage


print("-----------------------------------")
print(" STEP1: start greedy        ")
print("-----------------------------------")

#----ComputeReducedOrderBasisFrom???(meshFile,snapshotsFile)


cmd_FF=["FreeFem++", scriptFreeFem,"-m", meshFile1,"-nev",str(nev),"-snap", snapshotsFile,"-tmpbase", tmpbaseFile]
print("hello")
print(cmd_FF)
print("end")
try:
    FNULL = open(os.devnull, 'w')
    ret = subprocess.run(cmd_FF,stdout=FNULL,stderr=subprocess.PIPE)
    ret.check_returncode()

except subprocess.CalledProcessError:
    retstr = "Error when calling Freefem++\n" + "    Returns error:\n" + str(ret.stderr)
    raise OSError(ret.returncode, retstr)

print("Files generated in "+dataFolder+ ":"+ tmpbaseFile)

print("-----------------------------------")
print(" STEP1: basis generated        ")
print("-----------------------------------")

""" 
-----------------------------------
Convert the basis in an numpy array
------------------------------------
""" 

# lire les VTK en python (ds des fichiers temporaires)
#array_basis=basisFileToArray(tmpbaseFile,nev)
array_list = []
for i in range(nev):
    array_list.append(VTKReadToNp(tmpbaseFile,i))

print("-----------------------------------")
print(" STEP1: Basis converted in numpy   ")
print("-----------------------------------")
#----
#return array_list

""" 
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
                                      ONLINE
----------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------
""" 
""" 
----------------------------
              nirb
----------------------------
""" 

#print(tmpbase)
#meshFile1= osp.join(os.getcwd(),'../test/data/mesh1.msh') #fin

scriptFreeFem=osp.join(externalFolder,'nirbonline.edp')

"""Input
"""
meshFile2 = osp.join(dataFolder,'mesh2.msh') #grossier
uH=osp.join(dataFolder,'soluH.txt')

print("-----------------------------------")
print(" STEP2: start Online nirb        ")
print("-----------------------------------")


try:
    FNULL = open(os.devnull, 'w')
    ret = subprocess.run(["FreeFem++", scriptFreeFem,
                          "-m1"   , meshFile1,
                          "-m2"   , meshFile2,
                          "-nev"      ,str(nev),
                          "-base", tmpbaseFile,
                          "-uH", uH,
                          "-output", dataFolder
                          ],
                          stdout=FNULL,
                          stderr=subprocess.PIPE)
    ret.check_returncode()
except subprocess.CalledProcessError:
    retstr = "Error when calling Freefem++\n" + "    Returns error:\n" + str(ret.stderr)
    raise OSError(ret.returncode, retstr)



print("-----------------------------------")
print(" STEP2: Nirb done                  ")
print("Solution file :"+uH+"generated in "+dataFolder)
print("-----------------------------------")


# Sortir des VTK (ds des fichiers temporaires)
#import numpy as np
#import vtk
#from vtk.util.numpy_support import vtk_to_numpy

# Loop over temporary VTK files
#array_list = []
#test1 = os.system("mv solution.txt ../test/data/")
#return "ok"



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
