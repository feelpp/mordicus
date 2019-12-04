# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.Containers.CompressedFormats import ModesAndCoefficients as MAC
from MordicusCore.OperatorCompressors import Regression
from MordicusCore.Containers import ProblemData
from MordicusCore.Containers import CollectionProblemData
from MordicusCore.Containers import Solution
from MordicusCore.DataCompressors import SnapshotPOD as SP



def test():
    
    numberOfNodes = 20
    nbeOfComponents = 3
    
    solution  = Solution.Solution("U", nbeOfComponents, numberOfNodes, True)
    snapshot  = np.ones(nbeOfComponents*numberOfNodes)
    snapshot2 = np.random.rand(nbeOfComponents*numberOfNodes)
    solution.AddSnapshot(0., snapshot)
    solution.AddSnapshot(1., snapshot2)
    solution.AddSnapshot(2., snapshot2)
    
    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)
    problemData.AddParameter(np.array([1., 1., 0.5, 0.25]), 0.)
    problemData.AddParameter(np.array([2., 2., 1.,  0.9]),  2.)
    
    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)
    
    reducedOrdrBasis = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-8)
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    SP.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")
    

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e+1))
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)    

        
    operatorCompressionData = Regression.OperatorCompressionOffline(collectionProblemData, "U", gpr)
    
    onlineProblemData = ProblemData.ProblemData()
    onlineProblemData.AddParameter(np.array([0., 2., 0.5, 0.25]), 0.)
    onlineProblemData.AddParameter(np.array([2., 1., 2.,  0.5]),  3.)
    
    OnlineTimeSequence = np.array([0., 3.])
    
    compressedSnapshots = MAC.ModesAndCoefficients(solution.GetSolutionName(), OnlineTimeSequence, solution.GetNbeOfComponents(), solution.GetPrimality())
    
    Regression.OnlineComputeRegression(onlineProblemData, operatorCompressionData, compressedSnapshots)
    
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
