from genericROM.IO import ZsetReader as ZR
from genericROM.Containers import ProblemData as PD
from genericROM.Containers import CollectionProblemData as CPD
from genericROM.Containers import Solution as S
from genericROM.Containers.Meshes import MeshTools as MT
from genericROM.DataCompressors import SnapshotPOD
import numpy as np

folder = "Computation1/"

inputFileName = folder + "cube.inp"
meshFileName = folder + "cube.geof"
solutionFileName = folder + "cube.ut"

reader = ZR.ZsetReader(inputFileName, meshFileName, solutionFileName)

mesh = reader.ReadMesh()
print("Mesh defined in "+meshFileName+" has been read")

outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()
solution = S.Solution(solutionName = "TP", nbeOfComponents = 1, numberOfNodes = mesh.GetNumberOfNodes(), primality = True)
print("Solutions "+solution.GetSolutionName()+" defined in "+solutionFileName+" has been read")


for i in range(outputTimeSequence.shape[0]-1):
    snapshot = reader.ReadSnapshot(solution.GetSolutionName(), outputTimeSequence[i], solution.GetPrimality())
    solution.AddSnapshot(time = outputTimeSequence[i], snapshot = snapshot)

problemData = PD.ProblemData()

problemData.AddSolution(solution)


collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.AddProblemData("myComputation", problemData)
print("A collectionProblemData with problemDatas "+str(collectionProblemData.GetProblemDatasTags())+" has been constructed")

#loading = ZR.ReadLoading(folder+"cube.inp")


l2ScalarProducMatrix = MT.ComputeL2ScalarProducMatrix(mesh, 1)
collectionProblemData.SetL2ScalarProducMatrix("TP", l2ScalarProducMatrix)

##################################################

reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "TP", 1.e-4)
collectionProblemData.AddReducedOrderBasis("TP", reducedOrdrBasis)
print("A reduced order basis has been computed has been constructed using SnapshotPOD")

SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "TP")
print("The solution has been compressed")

from genericROM.IO import PXDMFWriter as PW
PW.WritePXDMF(mesh, solution.GetCompressedSnapshots())
print("The compressed solution has been written in PXDMF Format")




