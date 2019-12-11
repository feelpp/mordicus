# -*- coding: utf-8 -*-
import numpy as np
from MordicusModules.safran.OperatorCompressors import NonlinearMechanics as NLM
from MordicusCore.Containers.CompressedFormats import ModesAndCoefficients as MAC
from MordicusCore.Containers import ProblemData
from MordicusCore.Containers import CollectionProblemData
from MordicusCore.Containers import Solution
from MordicusCore.DataCompressors import SnapshotPOD as SP


def test():

    numberOfNodes = 20
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.random.rand(nbeOfComponents * numberOfNodes)
    solution.AddSnapshot(0.0, snapshot)
    solution.AddSnapshot(1.0, snapshot2)
    solution.AddSnapshot(2.0, snapshot2)

    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)
    problemData.AddParameter(np.array([1.0, 1.0, 0.5, 0.25]), 0.0)
    problemData.AddParameter(np.array([2.0, 2.0, 1.0, 0.9]), 2.0)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)

    reducedOrdrBasis = SP.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.0e-8
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    SP.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = 1.0 * RBF(
        length_scale=100.0, length_scale_bounds=(1e-2, 1e3)
    ) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e1))
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)

    operatorCompressionData = NLM.OperatorCompressionOffline(
        collectionProblemData, "U", gpr
    )

    onlineProblemData = ProblemData.ProblemData()
    onlineProblemData.AddParameter(np.array([0.0, 2.0, 0.5, 0.25]), 0.0)
    onlineProblemData.AddParameter(np.array([2.0, 1.0, 2.0, 0.5]), 3.0)

    OnlineTimeSequence = np.array([0.0, 3.0])

    compressedSnapshots = MAC.ModesAndCoefficients(
        solution.GetSolutionName(),
        OnlineTimeSequence,
        solution.GetNbeOfComponents(),
        solution.GetPrimality(),
    )

    NLM.OnlineComputeRegression(
        onlineProblemData, operatorCompressionData, compressedSnapshots
    )

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
