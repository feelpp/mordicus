from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.DataCompressors import SnapshotPOD
import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)



    folder = "Computation1/"

    inputFileName = folder + "cube.inp"
    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"

    meshReader = ZMR.ZsetMeshReader(meshFileName)
    inputReader = ZIR.ZsetInputReader(inputFileName)
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)

    matFiles = inputReader.ReadMaterialFiles()
    print("matFiles =", matFiles)

    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")

    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
    solution = S.Solution(
        solutionName="U",
        nbeOfComponents=mesh.GetDimensionality(),
        numberOfNodes=mesh.GetNumberOfNodes(),
        primality=True,
    )
    print(
        "Solutions "
        + solution.GetSolutionName()
        + " defined in "
        + solutionFileName
        + " has been read"
    )


    for i in range(outputTimeSequence.shape[0] - 1):
        snapshot = np.empty(mesh.GetDimensionality() * mesh.GetNumberOfNodes())
        for j in range(solution.GetNbeOfComponents()):
            snapshot[
                j * mesh.GetNumberOfNodes() : (j + 1) * mesh.GetNumberOfNodes()
            ] = solutionReader.ReadSnapshot(
                solution.GetSolutionName() + str(j + 1),
                outputTimeSequence[i],
                solution.GetPrimality(),
            )
        solution.AddSnapshot(time=outputTimeSequence[i], snapshot=snapshot)

    problemData = PD.ProblemData("myComputation")

    problemData.AddSolution(solution)


    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)
    print(
        "A collectionProblemData with problemDatas "
        + str(collectionProblemData.GetProblemDatasTags())
        + " has been constructed"
    )


    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)

    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.0e-4
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")
    print("The solution has been compressed")

    from Mordicus.Modules.Safran.IO import PXDMFWriter as PW

    PW.WritePXDMFFromSolution(mesh, solution, reducedOrderBasis)
    print("The compressed solution has been written in PXDMF Format")
    


    os.chdir(initFolder)    

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
