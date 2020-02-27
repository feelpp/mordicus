from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical
from Mordicus.Core.IO import StateIO as SIO
import numpy as np




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



print("PreCompressOperator...")
operatorPreCompressionData = Mechanical.PreCompressOperator(mesh)
print("...done")


outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()


solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)

for time in outputTimeSequence:
    U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
    solutionU.AddSnapshot(U, time)
    sigma = solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False)
    solutionSigma.AddSnapshot(sigma, time)



problemData = PD.ProblemData(folder)

problemData.AddSolution(solutionU)
problemData.AddSolution(solutionSigma)

collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.addVariabilityAxis('config', 
                                         str,
                                         description="dummy variability")
collectionProblemData.defineQuantity("U", "displacement", "m")
collectionProblemData.AddProblemData(problemData, config="case-1")

print("ComputeL2ScalarProducMatrix...")
snapshotCorrelationOperator = FT.ComputeL2ScalarProducMatrix(mesh, 3)

SP.CompressData(collectionProblemData, "U", 1.e-4, snapshotCorrelationOperator)
collectionProblemData.CompressSolutions("U", snapshotCorrelationOperator)
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")



solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
solutionUApprox.SetCompressedSnapshots(solutionU.GetCompressedSnapshots())
solutionUApprox.UncompressSnapshots(reducedOrderBasisU)

compressionErrors = []

for t in outputTimeSequence:
    exactSolution = solutionU.GetSnapshotAtTime(t)
    approxSolution = solutionUApprox.GetSnapshotAtTime(t)
    norml2ExactSolution = np.linalg.norm(exactSolution)
    if norml2ExactSolution != 0:
        relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
    else:
        relError = np.linalg.norm(approxSolution-exactSolution)
    compressionErrors.append(relError)

print("compressionErrors =", compressionErrors)

Mechanical.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-3)

print("CompressOperator done")

SIO.SaveState("collectionProblemData", collectionProblemData)
SIO.SaveState("snapshotCorrelationOperator", snapshotCorrelationOperator)



