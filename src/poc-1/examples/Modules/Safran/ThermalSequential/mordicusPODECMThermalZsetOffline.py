from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Thermal_transient as Th
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)


    folder = "ThermalSequential/"

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
    nbeOfComponentsPrimal = 1


    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()


    solutionT = S.Solution("TP", nbeOfComponentsPrimal, numberOfNodes, primality = True)

    for time in outputTimeSequence:
        T = solutionReader.ReadSnapshot("TP", time, nbeOfComponentsPrimal, primality=True)
        solutionT.AddSnapshot(T, time)


    problemData = PD.ProblemData(folder)
    problemData.AddSolution(solutionT)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)

    print("ComputeL2ScalarProducMatrix...")
    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 1)
    collectionProblemData.SetSnapshotCorrelationOperator("TP", l2ScalarProducMatrix)

    reducedOrderBasisT = SP.ComputeReducedOrderBasisFromCollectionProblemData(
            collectionProblemData, "TP", 1.e-4
    )
    collectionProblemData.AddReducedOrderBasis("TP", reducedOrderBasisT)
    collectionProblemData.CompressSolutions("TP")


    CompressedSolutionT = solutionT.GetCompressedSnapshots()

    compressionErrors = []

    for t in outputTimeSequence:
        reconstructedCompressedSolution = np.dot(CompressedSolutionT[t], reducedOrderBasisT)
        exactSolution = solutionT.GetSnapshot(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
        compressionErrors.append(relError)

    print("compressionErrors =", compressionErrors)

    Th.CompressOperator(
            collectionProblemData, mesh, 1.e-3
    )

    print("CompressOperator done")

    collectionProblemData.SaveState("mordicusState")

    os.chdir(initFolder)

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
