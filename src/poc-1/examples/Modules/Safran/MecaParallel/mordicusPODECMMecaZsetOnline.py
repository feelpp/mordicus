from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Modules.Safran.IO import ZsetSolutionWriter as ZSW
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical as Meca
from Mordicus.Core.IO import StateIO as SIO
import numpy as np



##################################################
# LOAD DATA FOR ONLINE
##################################################

collectionProblemData = SIO.LoadState("collectionProblemData")
operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")

operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")



##################################################
# ONLINE
##################################################


folder = "MecaParallel/"
inputFileName = folder + "cube.inp"
inputReader = ZIR.ZsetInputReader(inputFileName)

meshFileName = folder + "cube.geof"
mesh = ZMR.ReadMesh(meshFileName)

onlineProblemData = PD.ProblemData(folder)

timeSequence = inputReader.ReadInputTimeSequence()

constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)

loadingList = inputReader.ConstructLoadingsList()
for loading in loadingList:
    loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasisU, operatorCompressionData)
onlineProblemData.AddLoading(loadingList)

initialCondition = inputReader.ConstructInitialCondition()
initialCondition.ReduceInitialSnapshot(reducedOrderBasisU, snapshotCorrelationOperator)

onlineProblemData.SetInitialCondition(initialCondition)

initOnlineCompressedSnapshot = initialCondition.GetReducedInitialSnapshot()

import time
start = time.time()
onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, initOnlineCompressedSnapshot, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)
print(">>>> DURATION ONLINE =", time.time() - start)





ZSW.WriteZsetSolution(mesh, meshFileName, "reduced", onlineCompressedSolution, reducedOrderBasisU, "U", primality = True)


