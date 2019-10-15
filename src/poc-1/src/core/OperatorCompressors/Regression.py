# -*- coding: utf-8 -*-
import numpy as np
import sklearn
from core.Containers.CompressedFormats import ModesAndCoefficients as MAC

def OnlineComputeRegression(onlineProblemData, operatorCompressionOutputData, compressedSnapshots):
    """
    Compute the online stage using the method of POD on the snapshots and a regression on the coefficients
    
    The parameters must have been initialized in onlineProblemData
    The time sequence in compressedSnapshots must have been initialized
    This function set the attribute "coefficients" of compressedSnapshots
    
    Parameters
    ----------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object 
    compressedSnapshots : ModesAndCoefficients
        compressed solution whose attribute "coefficients" is set
    """
    regressor          = operatorCompressionOutputData[0]
    scalerParameter    = operatorCompressionOutputData[1]
    scalerCoefficients = operatorCompressionOutputData[2]
    
    timeSequence = compressedSnapshots.GetTimes()

    onlineParameters = np.array([onlineProblemData.GetParameterAtTime(t) for t in timeSequence])
    
    onlineParameters   = scalerParameter.transform(onlineParameters)
    onlineCoefficients = regressor.predict(onlineParameters)
    onlineCoefficients = scalerCoefficients.inverse_transform(onlineCoefficients)
    
    compressedSnapshots.SetCoefficients(onlineCoefficients)



def OperatorCompressionOffline(collectionProblemData, solutionName, operatorCompressionInputData):
    """
    Computes the offline operator compression stage using the method of POD on the snapshots and a regression on the coefficients
    
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object 
    solutionName : str
        name of the solution to be treated
    operatorCompressionInputData : class satisfying the scikit-learn regressors API
        input regressor to be fitted
                
    Returns
    -------
    operatorCompressionOutputData : (regressor, scaler, scaler)
        (fitted regressor, fitted scaler on the coefficients, fitted scaler on the parameters)
    """    
    assert isinstance(solutionName,str)
    
    regressor = operatorCompressionInputData
    
    numberOfModes      = collectionProblemData.GetReducedOrderBasisNumberOfModes(solutionName)
    numberOfSnapshots  = collectionProblemData.GetGlobalNumberOfSnapshots(solutionName)
    parameterDimension = collectionProblemData.GetParameterDimension()
    
    #print("numberOfModes      =", numberOfModes)
    #print("numberOfSnapshots  =", numberOfSnapshots)
    #print("parameterDimension =", parameterDimension)
    
    coefficients = np.zeros((numberOfSnapshots, numberOfModes))
    parameters   = np.zeros((numberOfSnapshots, parameterDimension))
    
    count = 0
    for key, problemData in collectionProblemData.GetProblemDatas().items():

        localNumberOfSnapshots = problemData.GetSolution(solutionName).GetNumberOfSnapshots()
        times = problemData.GetSolution(solutionName).GetCompressedSnapshots().GetTimes()
        
        coefficients[count:count+localNumberOfSnapshots,:] = problemData.GetSolution(solutionName).GetCompressedSnapshots().GetCoefficients()
        
        localParameters = np.array([problemData.GetParameterAtTime(t) for t in times])
        parameters[count:count+localNumberOfSnapshots,:] = localParameters
        
        count += localNumberOfSnapshots

    
    from sklearn.preprocessing import MinMaxScaler

    scalerParameter    = MinMaxScaler()
    scalerCoefficients = MinMaxScaler()
    
    scalerParameter.fit(parameters)
    scalerCoefficients.fit(coefficients)

    parameters = scalerParameter.transform(parameters)
    coefficients = scalerCoefficients.transform(coefficients)

    regressor.fit(parameters, coefficients)

    operatorCompressionOutputData = (regressor, scalerParameter, scalerCoefficients)

    return operatorCompressionOutputData



def CheckIntegrity():
    
    
    from BasicTools.Containers.UnstructuredMeshTools import CreateCube
    from modules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
    from core.Containers import ProblemData
    from core.Containers import CollectionProblemData
    from core.Containers import Solution
    from core.DataCompressors import SnapshotPOD as SP
    
    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3,4,3],spacing=[2.,2.,2.],ofTetras=True))
    
    nbeOfComponents = 3
    
    solution  = Solution.Solution("U", nbeOfComponents, mesh.GetNumberOfNodes(), True)
    snapshot  = np.ones(nbeOfComponents*mesh.GetNumberOfNodes())
    snapshot2 = np.random.rand(nbeOfComponents*mesh.GetNumberOfNodes())
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

        
    operatorCompressionData = OperatorCompressionOffline(collectionProblemData, "U", gpr)
    
    onlineProblemData = ProblemData.ProblemData()
    onlineProblemData.AddParameter(np.array([0., 2., 0.5, 0.25]), 0.)
    onlineProblemData.AddParameter(np.array([2., 1., 2.,  0.5]),  3.)
    
    OnlineTimeSequence = np.array([0., 3.])
    
    compressedSnapshots = MAC.ModesAndCoefficients(solution.GetSolutionName(), OnlineTimeSequence, solution.GetNbeOfComponents(), solution.GetPrimality())
    
    OnlineComputeRegression(onlineProblemData, operatorCompressionData, compressedSnapshots)
    
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
