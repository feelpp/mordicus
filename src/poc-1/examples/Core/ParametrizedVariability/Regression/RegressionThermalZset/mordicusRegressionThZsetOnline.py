from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Core.Helpers import FolderHandler as FH
import numpy as np
from pathlib import Path
import os


def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################

    collectionProblemData = SIO.LoadState("collectionProblemData")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("TP")


    ##################################################
    # ONLINE
    ##################################################

    onlineProblemData = PD.ProblemData("Online")

    OnlineTimeSequence = np.array(np.arange(200, 1001, 200), dtype=float)

    for t in OnlineTimeSequence:
        onlineProblemData.AddParameter(np.array([95.0, 950.0] + [t]), t)


    compressedSnapshots = Regression.ComputeOnline(
        onlineProblemData, operatorCompressionData
    )


    mesh = ZMR.ReadMesh("cube.geof")

    PW.WritePXDMF(mesh, compressedSnapshots, reducedOrderBasis, "TP")
    print("The compressed solution has been written in PXDMF Format")



    ##################################################
    #check accuracy of prediction
    ##################################################

    from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR

    numberOfNodes = reducedOrderBasis.shape[1]
    solutionName = "TP"
    nbeOfComponents = 1
    primality = True

    solutionFileName = "Online/cube.ut"
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName=solutionFileName)

    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

    solution = S.Solution(
        solutionName=solutionName,
        nbeOfComponents=nbeOfComponents,
        numberOfNodes=numberOfNodes,
        primality=primality,
    )
    for t in outputTimeSequence:
        snapshot = solutionReader.ReadSnapshot(
            solution.GetSolutionName(), t, solution.GetPrimality()
        )
        solution.AddSnapshot(snapshot, t)


    compressionErrors = []

    for t in OnlineTimeSequence:

        reconstructedCompressedSolution = np.dot(compressedSnapshots[t], reducedOrderBasis)
        exactSolution = solution.GetSnapshot(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
        compressionErrors.append(relError)

    folderHandler.SwitchToExecutionFolder()

    assert np.max(compressionErrors) < 0.12, "!!! Regression detected !!! compressionErrors have become too large"



if __name__ == "__main__":
    test()
