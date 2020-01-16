from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanics as Meca
import numpy as np
from pathlib import Path
import os


initFolder = os.getcwd()
currentFolder = str(Path(__file__).parents[0])
os.chdir(currentFolder)


folder = "MecaParallel/"

inputFileName = folder + "cube.inp"
meshFileName = folder + "cube.geof"
solutionFileName = folder + "cube.ut"

meshReader = ZMR.ZsetMeshReader(meshFileName)
inputReader = ZIR.ZsetInputReader(inputFileName)
solutionReader = ZSR.ZsetSolutionReader(solutionFileName)


mesh = meshReader.ReadMesh()
print("Mesh defined in " + meshFileName + " has been read")



numberOfNodes = mesh.GetNumberOfNodes()
numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
nbeOfComponentsPrimal = 3
nbeOfComponentsDual = 6

    
outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
    

solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)

for time in outputTimeSequence:
    U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
    solutionU.AddSnapshot(U, time)
    sigma = solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False)
    solutionSigma.AddSnapshot(sigma, time)


#solutionReader.ReadSnapshotTimeSequenceAndAddToSolution(solutionU, outputTimeSequence, "U")
#solutionReader.ReadSnapshotTimeSequenceAndAddToSolution(solutionSigma, outputTimeSequence, "sig")


problemData = PD.ProblemData(folder)
problemData.AddSolution(solutionU)
problemData.AddSolution(solutionSigma)

collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.AddProblemData(problemData)
    
print("ComputeL2ScalarProducMatrix...")
l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)
    
reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.e-4
)
collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
collectionProblemData.CompressSolutions("U")


CompressedSolutionU = solutionU.GetCompressedSnapshots()

compressionErrors = []

for t in outputTimeSequence:
    reconstructedCompressedSolution = np.dot(CompressedSolutionU[t], reducedOrderBasisU)
    exactSolution = solutionU.GetSnapshot(t)
    norml2ExactSolution = np.linalg.norm(exactSolution)
    if norml2ExactSolution != 0:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
    else:
        relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
    compressionErrors.append(relError)

print("compressionErrors =", compressionErrors)

Meca.CompressMecaOperator(
        collectionProblemData, mesh, 1.e-3
)

print("CompressMecaOperator done")

collectionProblemData.SaveState("mordicusState")

os.chdir(initFolder)    


