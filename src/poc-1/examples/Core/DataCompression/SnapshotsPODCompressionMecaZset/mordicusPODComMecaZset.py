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

    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")

    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
    

    solution = S.Solution("U", mesh.GetDimensionality(), mesh.GetNumberOfNodes(), primality = True)
    for time in outputTimeSequence[:-1]:
        U = solutionReader.ReadSnapshot("U", time, mesh.GetDimensionality(), primality=True)
        solution.AddSnapshot(U, time)
    
    problemData = PD.ProblemData(folder)

    problemData.AddSolution(solution)


    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)
    print(
        "A collectionProblemData with problemDatas "
        + str(collectionProblemData.GetProblemDatasFolders())
        + " has been constructed"
    )


    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)

    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.e-4
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    collectionProblemData.CompressSolutions("U")
    print("The solution has been compressed")

    from Mordicus.Modules.Safran.IO import PXDMFWriter as PW

    PW.WritePXDMFFromSolution(mesh, solution, reducedOrderBasis)
    print("The compressed solution has been written in PXDMF Format")
    


    os.chdir(initFolder)    

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
