from MordicusModules.safran.IO import ZsetReader as ZR
from MordicusCore.Containers import ProblemData as PD
from MordicusCore.Containers import CollectionProblemData as CPD
from MordicusCore.Containers.CompressedFormats import ModesAndCoefficients as MAC
from MordicusCore.Containers import Solution as S
from MordicusCore.DataCompressors import SnapshotPOD
from MordicusCore.OperatorCompressors import Regression
import numpy as np



    
mesh = ZR.ReadMesh("cube.geof")
numberOfNodes = mesh.GetNumberOfNodes()
solutionName = "TP"
nbeOfComponents = 1
primality = True

collectionProblemData = CPD.CollectionProblemData()

parameters = [[100., 1000.], [50., 3000.], [150., 300.], [130., 2000.]]

for i in range(4):
    folder = "Computation"+str(i+1)+"/"
    solutionFileName = folder + "cube.ut"
    reader = ZR.ZsetReader(solutionFileName = solutionFileName)

    outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()

    solution = S.Solution(solutionName = solutionName, nbeOfComponents = nbeOfComponents, numberOfNodes = numberOfNodes, primality = primality)

    problemData = PD.ProblemData()
    problemData.AddSolution(solution)

    parameter = parameters[i]
    for t in outputTimeSequence:
        snapshot = reader.ReadSnapshot(solution.GetSolutionName(), t, solution.GetPrimality())
        solution.AddSnapshot(t, snapshot)
        problemData.AddParameter(np.array(parameters[i] + [t]), t)

    collectionProblemData.AddProblemData(folder, problemData)
    

print("Solutions have been read")    

##################################################
# OFFLINE
##################################################

reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, solutionName, 1.e-4)
collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)
print("A reduced order basis has been computed has been constructed using SnapshotPOD")

SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "TP")
print("The solution has been compressed")



from sklearn.gaussian_process.kernels import WhiteKernel, RBF
from sklearn.gaussian_process import GaussianProcessRegressor

kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e+1))
gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)    

    
operatorCompressionData = Regression.OperatorCompressionOffline(collectionProblemData, solutionName, gpr)


##################################################
# SAVE DATA FOR ONLINE
##################################################

import pickle

output = open('operatorCompressionData.pkl', 'wb')
pickle.dump(operatorCompressionData, output)
output.close()

output = open('reducedOrderBasis.pkl', 'wb')
pickle.dump(reducedOrderBasis, output)
output.close()


