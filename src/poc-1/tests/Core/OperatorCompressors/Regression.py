# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#
import pytest
import numpy as np
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD as SP

@pytest.mark.skip(reason="currently fails")
def test_operator_compressor():

    numberOfNodes = 20
    nbeOfComponents = 3

    solution = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot = np.ones(nbeOfComponents * numberOfNodes)
    snapshot2 = np.random.rand(nbeOfComponents * numberOfNodes)
    solution.AddSnapshot(snapshot, 0.0)
    solution.AddSnapshot(snapshot, 0.5)
    solution.AddSnapshot(snapshot2, 1.0)
    solution.AddSnapshot(snapshot2, 2.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)
    problemData.AddParameter(np.array([1.0, 1.0, 0.5, 0.25]), 0.0)
    problemData.AddParameter(np.array([1.0, 1.5, 0.5, 0.25]), 0.5)
    problemData.AddParameter(np.array([2.0, 0.5, 1.0, 0.9]), 1.0)
    problemData.AddParameter(np.array([2.0, 2.0, 1.0, 0.9]), 2.0)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis("config", str)
    collectionProblemData.DefineQuantity("U")
    collectionProblemData.AddProblemData(problemData, config="case-1")

    reducedOrdrBasis = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.0e-8)
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    collectionProblemData.CompressSolutions("U")

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF, ConstantKernel
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(0.01, 10.0)) * RBF(length_scale_bounds=(1e-2, 1e2)) + WhiteKernel(noise_level_bounds=(1e-10, 1e0))

    regressors = {"U":GaussianProcessRegressor(kernel=kernel)}

    paramGrids = {}
    paramGrids["U"] = {'kernel__k1__k1__constant_value':[0.1, 1.], 'kernel__k1__k2__length_scale': [1., 10.], 'kernel__k2__noise_level': [1., 2.]}

    Regression.CompressOperator(collectionProblemData, regressors, paramGrids)

    onlineProblemData = ProblemData.ProblemData("Online")
    onlineProblemData.AddParameter(np.array([0.0, 2.0, 0.5, 0.25]), 0.0)
    onlineProblemData.AddParameter(np.array([2.0, 1.0, 2.0, 0.5]), 3.0)

    operatorCompressionData = collectionProblemData.GetOperatorCompressionData("U")
    onlineProblemData.AddOnlineData(operatorCompressionData)

    Regression.ComputeOnline(onlineProblemData, "U")

    return "ok"


if __name__ == "__main__":
    print(test_operator_compressor()())  # pragma: no cover
