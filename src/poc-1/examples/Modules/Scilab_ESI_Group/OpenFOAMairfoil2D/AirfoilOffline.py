from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Scilab_ESI_Group import SciSolutionReader as SSR
from sklearn.gaussian_process.kernels import WhiteKernel, RBF
from sklearn.gaussian_process import GaussianProcessRegressor
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.IO import StateIO as SIO
import numpy as np
from pathlib import Path
import os

def test():
    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)

    ####################################################
    # DEFINE READERS
    ####################################################
    solutionFileName = "data/my2Dpressure.csv"
    solutionReader = SSR.SciSolutionReader(solutionFileName)

    ####################################################
    # DEFINE COLLECTION PROBLEM DATA ARCHITECTURE
    ####################################################
    collectionProblemData = CPD.CollectionProblemData()
    # ADD? DOE = SCENARIO1 SCENARIO2 ... SCENARIO10
    collectionProblemData.addVariabilityAxis('mu1',float,description="my_parameter")
    collectionProblemData.defineQuantity("P", full_name="pressure", unit="Pa")

    nbOfComp = 1
    nbOfNodes = 10906
    #nbOfNodes = mesh.GetNumberOfNodes()

    nbRuns = 21
    parameter = range(-10, 11)
    for i in range(nbRuns):
        ####################################################
        # DEFINE PROBLEM ARCHITECTURE
        ####################################################
        Scenario = "SCENARIO" + str(i)
        problemData = PD.ProblemData(Scenario)

        ####################################################
        # DEFINE SOLUTION ARCHITECTURE
        ####################################################
        solutionP = S.Solution("P", nbOfComp, nbOfNodes, primality=True)

        ####################################################
        # FILL SOLUTION & PROBLEM OBJECT & COLLECTION PB OBJECT
        ####################################################
        snapshot = solutionReader.ReadSnapshotComponent("P", i, primality=True)
        solutionP.AddSnapshot(snapshot, 0)
        # Fill DOE
        problemData.AddParameter(np.array([parameter[i]]), 0)
        problemData.AddSolution(solutionP)
        collectionProblemData.AddProblemData(problemData,mu1=float(parameter[i]))

    ####################################################
    # FILL COLLECTION PROBLEM WITH OFFLINE
    ####################################################

    ## DEFINE INNER PRODUCT (default is EUCLIDEAN)
    # l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    # collectionProblemData.SetSnapshotCorrelationOperator("P", l2ScalarProducMatrix)

    ## NORMALIZED SVD ON CORRELATION MATRIX (SNAPSHOT METHOD)
    reducedOrderBasisP = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "P", 1.0e-4)
    collectionProblemData.AddReducedOrderBasis("P", reducedOrderBasisP)

    ## COMPUTE PROJECTED COEFFICIENTS
    collectionProblemData.CompressSolutions("P")

    ## RECONSTRUCT SOLUTION FROM COEFFICIENTS
    #CompressedSolutionP = solutionP.GetCompressedSnapshots()
    #print(CompressedSolutionP)

    ## REGRESSION = COMPRESS OPERATOR
    kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e1))
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)
    # Training
    Regression.CompressOperator(collectionProblemData, "P", gpr)
    # NOTA: Le compressOperator est associe au collectionProblemData. Pas evident!
    # D'autant qu'on réutilise Regression pour calculer les snapshots compresses. Faire de regression un container ?

    ####################################################
    # SAVE DATA
    ####################################################
    SIO.SaveState("collectionProblemData", collectionProblemData)

    ####################################################
    # TEST
    ####################################################
    os.chdir(initFolder)

    return "ok"

if __name__ == "__main__":
    print(test())
