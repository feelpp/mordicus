# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD as SP


def test():

    numberOfNodes = 20
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.random.rand(nbeOfComponents * numberOfNodes)
    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot2, 1.0)
    solution.AddSnapshot(snapshot2, 2.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)
    problemData.AddParameter(np.array([1.0, 1.0, 0.5, 0.25]), 0.0)
    problemData.AddParameter(np.array([2.0, 2.0, 1.0, 0.9]), 2.0)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)

    reducedOrdrBasis = SP.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.0e-8
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    collectionProblemData.CompressSolutions("U")

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = 1.0 * RBF(
        length_scale=100.0, length_scale_bounds=(1e-2, 1e3)
    ) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e1))
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)

    Regression.CompressOperator(
        collectionProblemData, "U", gpr
    )

    onlineProblemData = ProblemData.ProblemData("Online")
    onlineProblemData.AddParameter(np.array([0.0, 2.0, 0.5, 0.25]), 0.0)
    onlineProblemData.AddParameter(np.array([2.0, 1.0, 2.0, 0.5]), 3.0)

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

    Regression.ComputeOnline(
        onlineProblemData, operatorCompressionData
    )

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
