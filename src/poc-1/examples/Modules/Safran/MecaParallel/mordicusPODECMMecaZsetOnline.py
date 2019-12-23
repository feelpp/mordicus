from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanics as Meca
import numpy as np
from pathlib import Path
import os



initFolder = os.getcwd()
currentFolder = str(Path(__file__).parents[0])
os.chdir(currentFolder)



##################################################
# LOAD DATA FOR ONLINE
##################################################

collectionProblemData = CPD.Load("mordicusState")

operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
snapshotCorrelationOperator = collectionProblemData.GetSnapshotCorrelationOperator("U")
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
    loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBasisU, snapshotCorrelationOperator, operatorCompressionData)
onlineProblemData.AddLoading(loadingList)



import time
start = time.time()
onlineCompressedSolution = Meca.ComputeOnline(onlineProblemData, timeSequence, reducedOrderBasisU, operatorCompressionData, 1.e-4)
print(">>>> DURATION ONLINE =", time.time() - start)


os.chdir(initFolder)    
