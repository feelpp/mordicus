from __future__ import print_function

from Mordicus.Modules.Phimeca.IO.OTSolutionReader import OTSolutionReader
from Mordicus.Modules.Phimeca.IO.OTMeshReader import OTMeshReader

from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD

import numpy as np
import openturns as ot

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

print("Create ProblemData...")
reader = OTMeshReader(ot_mesh)
mesh = reader.ReadMesh()

numberOfNodes = mesh.GetNumberOfNodes()
nbeOfComponents = outputSample.getDimension()
primality = True

dataFolder = '.'
problemData = PD.ProblemData(dataFolder)

solutionZ = S.Solution('Z', nbeOfComponents, numberOfNodes, primality)
problemData.AddSolution(solutionZ)

for i in range(size):
    solutionReader = OTSolutionReader(outputSample)
    #print(outputSample[i].getValues()[:5])

    # FIXME: indexing variable is not time, it is just the id of the realization, but we have to cast it to a float
    time = float(i)
    print('time=', time)
    snapshot = solutionReader.ReadSnapshotComponent(solutionZ.GetSolutionName(), time, solutionZ.GetPrimality())
    #print(snapshot.shape)

    solutionZ.AddSnapshot(snapshot, time)

    parameter = np.array(inputSample[i])
    problemData.AddParameter(parameter, time)



collectionProblemData = CPD.CollectionProblemData()
collectionProblemData.AddProblemData(problemData)



#print("ComputeL2ScalarProducMatrix...")
#l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
#collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)

#reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(
        #collectionProblemData, "U", 1.e-4
#)
#collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
#collectionProblemData.CompressSolutions("U")



#solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
#solutionUApprox.SetCompressedSnapshots(solutionU.GetCompressedSnapshots())
#solutionUApprox.UncompressSnapshots(reducedOrderBasisU)

#compressionErrors = []

#for t in outputTimeSequence:
    #exactSolution = solutionU.GetSnapshotAtTime(t)
    #approxSolution = solutionUApprox.GetSnapshotAtTime(t)
    #norml2ExactSolution = np.linalg.norm(exactSolution)
    #if norml2ExactSolution != 0:
        #relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
    #else:
        #relError = np.linalg.norm(approxSolution-exactSolution)
    #compressionErrors.append(relError)

#print("compressionErrors =", compressionErrors)

#Meca.CompressOperator(
        #collectionProblemData, mesh, 1.e-3
#)

#print("CompressOperator done")

#collectionProblemData.SaveState("mordicusState")

#os.chdir(initFolder)




# wget -c --no-check-certificate https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -P /tmp
# bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p $PWD/miniconda
# export PATH=$PWD/miniconda/bin:$PATH
# conda config --add channels conda-forge
# conda config --set channel_priority strict
# conda update conda
# conda create --name mordicus python=3.8
# conda install -c conda-forge pytest pytest-cov mpi4py appdirs scikit-learn scikit-sparse numpy scipy vtk sympy pyamg h5py pyparsing Cython sphinx setuptools pylint black


# cd tests/Core && PYTHONPATH=../../src pytest --cov=../../src/Mordicus/Core --cov-report=html:../../coverageReports/coverageReportCore
# cd tests/Modules/Safran && PYTHONPATH=../../../src/ pytest --cov=../../../src/Mordicus/Modules/Safran --cov-report=html:../../../coverageReports/coverageReportCore
# cd tests/Modules/Phimeca && PYTHONPATH=../../../src/ pytest --cov=../../../src/Mordicus/Modules/Phimeca --cov-report=html:../../../coverageReports/coverageReportCore
# PYTHONPATH=$PWD/src python examples/Modules/Phimeca/ViscousFall/main.py
