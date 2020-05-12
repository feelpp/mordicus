import os
import os.path as osp

import subprocess

from Mordicus.Modules.sorbonne.IO import GmshMeshReader as GMR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.FE import FETools as FT

#from tkinter.constants import CURRENT
#from Mordicus.Modules.sorbonne.IO import FFSolutionReader
from initCase import initproblem
from initCase import basisFileToArray
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
dataFolder=osp.join(currentFolder,'StationaryNSData')
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
import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
nev=3    #nombre de modes         
time=0.0 
dimension=2
           
# instancie a reader solution           
#solreader = FFSolutionReader.FFSolutionReaderBase("Velocity")

array_list = []


## On lit le maillage ici si deja GMSH et sinon on convertit d'abord en GMSH pour le lire ensuite avec basictools
meshFileName = dataFolder + "/mesh1GMSH.msh"
print(meshFileName)
meshFile=open(meshFileName,"r")
premiereligne=meshFile.readline()
print("ici!",premiereligne[1:-1])

premierelignebis="MeshFormat"
if premiereligne[1:-1] == premierelignebis[:]: #si c'est au format GMSH 
    print("GMSH format")
    meshFileNameGMSH = dataFolder + "/mesh1GMSH.msh"
    os.rename(meshFileName, meshFileNameGMSH)
else: #si c'est format FF++, on convertir au format GMSH
    #ici appel de ff++ pour convertir
    print("FF++ format...")
    scriptPythonConvert=osp.join(externalFolder,'Converter.py')
    meshFileNameconv = dataFolder + "/mesh1GMSH.msh"
    cmd_py=["python", scriptPythonConvert,meshFileName,"-o", meshFileNameconv]
    print("Converted")
    try:
        FNULL = open(os.devnull, 'w')
        ret = subprocess.run(cmd_py,stdout=FNULL,stderr=subprocess.PIPE)
        ret.check_returncode()
    except subprocess.CalledProcessError:
        retstr = "Error when calling Python\n" + "    Returns error:\n" + str(ret.stderr)
        raise OSError(ret.returncode, retstr)

    
meshFileName = dataFolder + "/mesh1GMSH.msh"
meshReader = GMR.GmshMeshReader(meshFileName)
mesh = meshReader.ReadMesh()
print(mesh)
print("Mesh defined in " + meshFileName + " has been read")
nbeOfComponentsPrimal = 2 # vitesses 2D
numberOfNodes = mesh.GetNumberOfNodes()
print("nbNodes",numberOfNodes)
print("dimmesh",mesh.GetDimensionality())
collectionProblemData = CPD.CollectionProblemData()
#solutionU=S.Solution("U",dimension,numberOfNodes,True)


for i in range(nev):
    
    reader=vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(dataFolder+"/snapshot"+str(i) + ".vtu")
    reader.Update()
    fdata = reader.GetOutput().GetPointData()
    u1_vtk_array = fdata.GetArray("u")
    u1_np_array = vtk_to_numpy(u1_vtk_array)
    array_list.append(u1_np_array)          
    
    #instancie une solution
    u1_np_array=u1_np_array.flatten()
    #print(u1_np_array.shape)
    solutionU=S.Solution("U",dimension,numberOfNodes,True)
    ### ajouter la snapshot A solutionU
    #solutionU=S.Solution("U",dimension,numberOfNodes,True)
    solutionU.AddSnapshot(u1_np_array,0)
    problemData = PD.ProblemData(dataFolder+str(i))
    problemData.AddSolution(solutionU)
    collectionProblemData.AddProblemData(problemData)


snapshotsIterator = collectionProblemData.SnapshotsIterator("U")

snapshots = []
for s in snapshotsIterator:

    snapshots.append(s)
print("snap",np.shape(snapshots))

numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
print(np.shape(numberOfIntegrationPoints))
""" POD """
print("ComputeL2ScalarProducMatrix...")
l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 2)
print("t",type(l2ScalarProducMatrix))
print("max",l2ScalarProducMatrix.max())
print(l2ScalarProducMatrix.min())

#collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)


reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-4)
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U")

compressionErrors=[]
for i in range(nev):

    problemData=collectionProblemData.GetProblemData(dataFolder+str(i))
    solutionU=problemData.GetSolution("U")

    #recuperer sur la solution pr chaque problemdata
    CompressedSolutionU = solutionU.GetCompressedSnapshots()

    reconstructedCompressedSolution = np.dot(CompressedSolutionU[0], reducedOrderBasisU) #pas de tps 0

    exactSolution = solutionU.GetSnapshot(0)
    norml2ExactSolution = np.linalg.norm(exactSolution)
    if norml2ExactSolution != 0:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
    else:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    compressionErrors.append(relError)
print("compressionErrors =", compressionErrors)

print("POD OK? ")



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

