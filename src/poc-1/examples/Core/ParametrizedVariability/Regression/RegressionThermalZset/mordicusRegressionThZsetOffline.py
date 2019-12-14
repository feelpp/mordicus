from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD
from Mordicus.Core.OperatorCompressors import Regression
import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)




    mesh = ZMR.ReadMesh("cube.geof")
    numberOfNodes = mesh.GetNumberOfNodes()
    solutionName = "TP"
    nbeOfComponents = 1
    primality = True

    collectionProblemData = CPD.CollectionProblemData()

    parameters = [[100.0, 1000.0], [50.0, 3000.0], [150.0, 300.0], [130.0, 2000.0]]

    for i in range(4):
        folder = "Computation" + str(i + 1) + "/"
        solutionFileName = folder + "cube.ut"
        solutionReader = ZSR.ZsetSolutionReader(solutionFileName=solutionFileName)

        outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

        solution = S.Solution(
            solutionName=solutionName,
            nbeOfComponents=nbeOfComponents,
            numberOfNodes=numberOfNodes,
            primality=primality,
        )

        problemData = PD.ProblemData(folder)
        problemData.AddSolution(solution)

        parameter = parameters[i]
        for t in outputTimeSequence:
            snapshot = solutionReader.ReadSnapshot(
                solution.GetSolutionName(), t, solution.GetPrimality()
            )
            solution.AddSnapshot(t, snapshot)
            problemData.AddParameter(np.array(parameters[i] + [t]), t)

        collectionProblemData.AddProblemData(problemData)


    print("Solutions have been read")

    ##################################################
    # OFFLINE
    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, solutionName, 1.0e-4
    )
    collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "TP")
    print("The solution has been compressed")


    from sklearn.gaussian_process.kernels import WhiteKernel, RBF
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(
        noise_level=1, noise_level_bounds=(1e-10, 1e1)
    )
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)


    Regression.CompressOperator(
        collectionProblemData, solutionName, gpr
    )

    collectionProblemData.Save("mordicusState")


    os.chdir(initFolder)    

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
