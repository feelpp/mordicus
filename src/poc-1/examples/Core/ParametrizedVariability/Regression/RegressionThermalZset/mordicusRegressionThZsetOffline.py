from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.IO import StateIO as SIO
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
    collectionProblemData.defineVariabilityAxes(['Text', 'Tint'], 
                                                [float, float],
                                                [('Temperature', 'Celsius')]*2,
                                                ['External temperature', 'Internal Temperature'])
    collectionProblemData.defineQuantity(solutionName, "Temperature", "Celsius")

    parameters = [[100.0, 1000.0], [90.0, 1100.0], [110.0, 900.0], [105.0, 1050.0]]

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


        for t in outputTimeSequence:
            snapshot = solutionReader.ReadSnapshot(
                solution.GetSolutionName(), t, solution.GetPrimality()
            )
            solution.AddSnapshot(snapshot, t)
            problemData.AddParameter(np.array(parameters[i] + [t]), t)

        collectionProblemData.AddProblemData(problemData, Text=parameters[i][0], Tint=parameters[i][1])


    print("Solutions have been read")

    ##################################################
    # OFFLINE
    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, solutionName, 1.e-2
    )
    collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    collectionProblemData.CompressSolutions("TP")
    print("The solution has been compressed")


    from sklearn.gaussian_process.kernels import WhiteKernel, RBF
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = 1.0 * RBF(length_scale=10.0, length_scale_bounds=(1e-2, 1e2)) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e0))

    gpr = GaussianProcessRegressor(kernel=kernel, alpha=1.0)


    Regression.CompressOperator(
        collectionProblemData, solutionName, gpr
    )

    SIO.SaveState("collectionProblemData", collectionProblemData)



    ##################################################
    ## check accuracy compression
    ##################################################

    compressionErrors = []

    for _, problemData in collectionProblemData.GetProblemDatas().items():
        solution = problemData.GetSolution("TP")
        CompressedSolution = solution.GetCompressedSnapshots()
        for t in solution.GetTimeSequenceFromCompressedSnapshots():
            reconstructedCompressedSnapshot = np.dot(CompressedSolution[t], reducedOrderBasis)
            exactSolution = solution.GetSnapshotAtTime(t)
            norml2ExactSolution = np.linalg.norm(exactSolution)
            if norml2ExactSolution != 0:
                relError = np.linalg.norm(reconstructedCompressedSnapshot-exactSolution)/norml2ExactSolution
            else:
                relError = np.linalg.norm(reconstructedCompressedSnapshot-exactSolution)
            compressionErrors.append(relError)


    os.chdir(initFolder)

    if np.max(compressionErrors) > 1.e-2:

        return "not ok"

    else:

        return "ok"



if __name__ == "__main__":
    print(test())  # pragma: no cover
