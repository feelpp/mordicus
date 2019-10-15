from safran.IO import ZsetReader as ZR
from core.Containers import ProblemData as PD
from core.Containers import CollectionProblemData as CPD
from core.Containers import Solution as S
from safran.Containers.Meshes import MeshTools as MT
from core.DataCompressors import SnapshotPOD
import numpy as np

folder = "Computation1/"

inputFileName = folder + "cube.inp"
meshFileName = folder + "cube.geof"
solutionFileName = folder + "cube.ut"

reader = ZR.ZsetReader(inputFileName, meshFileName, solutionFileName)

mesh = reader.ReadMesh()
print("Mesh defined in "+meshFileName+" has been read")

outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()
solution = S.Solution(solutionName = "U", nbeOfComponents = mesh.GetDimensionality(), numberOfNodes = mesh.GetNumberOfNodes(), primality = True)
print("Solutions "+solution.GetSolutionName()+" defined in "+solutionFileName+" has been read")


for i in range(outputTimeSequence.shape[0]-1):
    snapshot = np.empty(mesh.GetDimensionality()*mesh.GetNumberOfNodes())
    for j in range(solution.GetNbeOfComponents()):
        snapshot[j*mesh.GetNumberOfNodes():(j+1)*mesh.GetNumberOfNodes()] = reader.ReadSnapshot(solution.GetSolutionName()+str(j+1), outputTimeSequence[i], solution.GetPrimality())
    solution.AddSnapshot(time = outputTimeSequence[i], snapshot = snapshot)

problemData = PD.ProblemData()

problemData.AddSolution(solution)


collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.AddProblemData("myComputation", problemData)
print("A collectionProblemData with problemDatas "+str(collectionProblemData.GetProblemDatasTags())+" has been constructed")



l2ScalarProducMatrix = MT.ComputeL2ScalarProducMatrix(mesh, 3)
collectionProblemData.SetL2ScalarProducMatrix("U", l2ScalarProducMatrix)

##################################################

reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-8)
collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
print("A reduced order basis has been computed has been constructed using SnapshotPOD")

SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")
print("The solution has been compressed")

from safran.IO import PXDMFWriter as PW
PW.WritePXDMF(mesh, solution.GetCompressedSnapshots())
print("The compressed solution has been written in PXDMF Format")




