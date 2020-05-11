from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Modules.Scilab_ESI_Group import SciSolutionReader as SSR
import numpy as np
from pathlib import Path
import os

def test():
    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)

    ####################################################
    # LOAD DATA FOR ONLINE
    ####################################################
    collectionProblemData = CPD.LoadState("mordicusState2")
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("P")
    #print(collectionProblemData.GetProblemData('.').GetParameters()) # Pas top!
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    
    ####################################################
    # DEFINE PREDICTED SOLUTION ARCHITECTURE
    ####################################################
    nbOfComp = 1
    nbOfNodes = 10906
    onlineSolution = S.Solution('P', nbOfComp, nbOfNodes, primality=True)
    # NOTA: Could be build using training Solution Object

    ####################################################
    # DEFINE PREDICTED PROBLEM ARCHITECTURE
    ####################################################
    onlineProblemData = PD.ProblemData("Online") # No need for folderpath
    onlineProblemData.AddSolution(onlineSolution)
    #ADD? API(CollectionProblemData) = onlineProblemData

    ####################################################
    # FILL SOLUTION & PROBLEM OBJECT
    ####################################################
    # New set of parameters
    newInputs = [1.2]
    onlineProblemData.AddParameter(np.array(newInputs), 0)
    # NOTA: Pas pratique quand parametre scalaire, car il faut ajouter des crochets
    # NOTA: Encore confusion entre temps et parametre

    ####################################################
    # FILL PREDICTED SOLUTION WITH ONLINE
    ####################################################
    import time
    start = time.time()
    ## COMPUTE COFFICIENTS WITH REGRESSION
    onlineCompressedSnapshots = Regression.ComputeOnline(onlineProblemData, operatorCompressionData)
    # NOTA: Confusion entre snapshots et coefficients?
    print(">>>> DURATION ONLINE =", time.time() - start)
    onlineSolution.SetCompressedSnapshots(onlineCompressedSnapshots)

    ## COMPUTE COMPRESSED SOLUTION FROM COEFFICIENTS
    onlineProblemData.UncompressSolution('P', reducedOrderBasis)

    ####################################################
    # VALIDATE
    ####################################################
    # newOutputs = onlineSolution.GetSnapshot(0)
    # print(newOutputs)

    ####################################################
    # EXPORT
    ####################################################
    # PW.WritePXDMF(mesh, onlineCompressedSnapshots, reducedOrderBasis, 'P')
    # print("The compressed solution has been written in PXDMF format")

    ####################################################
    # TEST
    ####################################################
    os.chdir(initFolder)

    return "ok"

if __name__ == "__main__":
    print(test())