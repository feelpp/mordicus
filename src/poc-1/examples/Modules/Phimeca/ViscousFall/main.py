from __future__ import print_function

from Mordicus.Modules.Phimeca.IO.OTSolutionReader import OTSolutionReader
from Mordicus.Modules.Phimeca.IO.OTMeshReader import OTMeshReader

from Mordicus.Core.Containers.ProblemData import ProblemData 
from Mordicus.Core.Containers.CollectionProblemData import CollectionProblemData
from Mordicus.Core.Containers.Solution import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Core.OperatorCompressors import Regression

import numpy as np
import openturns as ot
from sklearn.gaussian_process.kernels import WhiteKernel, RBF
from sklearn.gaussian_process import GaussianProcessRegressor

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


# Some parameters
tmin=0.0 # start time
tmax=12. # end time
gridsize=100 # number of time steps
ot_mesh = ot.IntervalMesher([gridsize-1]).build(ot.Interval(tmin, tmax))

# model function
def AltiFunc(X):
    g  = 9.81
    z0 = X[0]
    v0 = X[1]
    m  = X[2]
    c  = X[3]
    zmin = X[4]
    tau=m/c
    vinf=-m*g/c
    t = np.linspace(tmin,tmax,gridsize)
    z=z0+vinf*t+tau*(v0-vinf)*(1-np.exp(-t/tau))
    z=np.maximum(z,zmin)
    return [[zeta] for zeta in z]
alti = ot.PythonPointToFieldFunction(5, ot_mesh, 1, AltiFunc)

# Creation of the input distribution
distZ0 = ot.Uniform(100.0, 150.0)
distV0 = ot.Normal(55.0, 10.0)
distM = ot.Normal(80.0, 8.0)
distC = ot.Uniform(0.0, 30.0)
distZmin = ot.Dirac([0.0])
distX = ot.ComposedDistribution([distZ0, distV0, distM, distC, distZmin])

# Sample the model
size = 10
inputSample = distX.getSample(size)
outputSample = alti(inputSample)

print("-- Create ProblemData...")
reader = OTMeshReader(ot_mesh)
mesh = reader.ReadMesh()

numberOfNodes = mesh.GetNumberOfNodes()
nbeOfComponents = outputSample.getDimension()
primality = True

dataFolder = '.'
problemData = ProblemData(dataFolder)

solutionZ = Solution('Z', nbeOfComponents, numberOfNodes, primality)
problemData.AddSolution(solutionZ)

for i in range(size):
    solutionReader = OTSolutionReader(outputSample)
    #print(outputSample[i].getValues()[:5])

    snapshot = solutionReader.ReadSnapshotComponent(solutionZ.GetSolutionName(), i, solutionZ.GetPrimality())
    #print(snapshot.shape)

    solutionZ.AddSnapshot(snapshot, i)

    parameter = np.array(inputSample[i])
    problemData.AddParameter(parameter, i)



collectionProblemData = CollectionProblemData()
collectionProblemData.defineVariabilityAxes(["Z0", "V0", "M", "C", "Zmin"],
                                            [float]*5,
                                            [("position", "m"), ("speed", "m/s"), ("mass", "Kg"), ("drag", "Kg/s"), ("position", "m")], 
                                            ["Initial altitude",
                                             "Initial speed",
                                             "Mass",
                                             "Drag coefficient",
                                             "Altitude of ground"])
collectionProblemData.defineQuantity("Z", "altitude", "m")

collectionProblemData.AddProblemData(problemData, Z0=inputSample[i][0],
                                                      V0=inputSample[i][1],
                                                      M=inputSample[i][2],
                                                      C=inputSample[i][3],
                                                      Zmin=float(inputSample[i][4]))

print("-- Offline...")
reducedOrderBasis = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "Z", 1.0e-8)
collectionProblemData.AddReducedOrderBasis("Z", reducedOrderBasis)
collectionProblemData.CompressSolutions("Z")

kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e1))
gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)

Regression.CompressOperator(collectionProblemData, "Z", gpr)

print("-- Online ...")
onlineProblemData = ProblemData("Online")
newInputs = distX.getSample(5)
for i in range(newInputs.getSize()):
    onlineProblemData.AddParameter(np.array(newInputs[i]), i)
onlineSolution = Solution('Z', nbeOfComponents, numberOfNodes, primality)
onlineProblemData.AddSolution(onlineSolution)
operatorCompressionData = collectionProblemData.GetOperatorCompressionData()

onlineCompressedSnapshots = Regression.ComputeOnline(onlineProblemData, operatorCompressionData)
onlineSolution.SetCompressedSnapshots(onlineCompressedSnapshots)
onlineProblemData.UncompressSolution('Z', reducedOrderBasis)
newOutputs = [onlineSolution.GetSnapshot(i) for i in range(newInputs.getSize())]

print("-- Plot training/new trajectories ...")
t = np.array(ot_mesh.getVertices())
for i in range(outputSample.getSize()):
    plt.plot(t, outputSample[i], color='blue', label='offline' if i==0 else '')
for i in range(newInputs.getSize()):
    plt.plot(t, newOutputs[i], color='red', label='online' if i==0 else '')
plt.title('viscous fall')
plt.legend()
plt.savefig('viscous_fall.png')
print("ok")

