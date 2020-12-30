from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Core.Helpers import FolderHandler as FH
import numpy as np
import pytest

@pytest.mark.mpi
def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()


    folder = "MecaParallelBiMat/"

    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"

    meshReader = ZMR.ZsetMeshReader(meshFileName)
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)


    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")



    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    nbeOfComponentsPrimal = 3
    nbeOfComponentsDual = 6



    print("PreCompressOperator...")
    operatorPreCompressionData = Mechanical.PreCompressOperator(mesh)
    print("...done")

    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

    dualNames = ["evrcum", "sig12", "sig23", "sig31", "sig11", "sig22", "sig33", "eto12", "eto23", "eto31", "eto11", "eto22", "eto33"]

    solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)

    solutionsDual = [S.Solution(name, 1, numberOfIntegrationPoints, primality = False) for name in dualNames]


    for time in outputTimeSequence:
        solutionU.AddSnapshot(solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True), time)
        solutionSigma.AddSnapshot(solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False), time)
        for i, name in enumerate(dualNames):
            solutionsDual[i].AddSnapshot(solutionReader.ReadSnapshotComponent(name, time, primality=False), time)



    problemData = PD.ProblemData(folder)

    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionSigma)

    for i, name in enumerate(dualNames):
        problemData.AddSolution(solutionsDual[i])


    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.addVariabilityAxis('config',
                                            str,
                                            description="dummy variability")
    collectionProblemData.defineQuantity("U", "displacement", "m")
    collectionProblemData.defineQuantity("sigma", "stress", "Pa")
    for i, name in enumerate(dualNames):
        collectionProblemData.defineQuantity(name)
    collectionProblemData.AddProblemData(problemData, config="case-1")


    print("ComputeL2ScalarProducMatrix...")
    snapshotCorrelationOperator = {}
    snapshotCorrelationOperator["U"] = FT.ComputeL2ScalarProducMatrix(mesh, 3)

    SP.CompressData(collectionProblemData, "U", 1.e-6, snapshotCorrelationOperator["U"])
    for name in dualNames:
        SP.CompressData(collectionProblemData, name, 1.e-6)


    collectionProblemData.CompressSolutions("U", snapshotCorrelationOperator["U"])
    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")


    CompressedSolutionU = solutionU.GetCompressedSnapshots()

    compressionErrors = []

    for t in outputTimeSequence:

        reconstructedCompressedSolution = np.dot(CompressedSolutionU[t], reducedOrderBasisU)
        exactSolution = solutionU.GetSnapshot(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
        compressionErrors.append(relError)

    print("compressionErrors =", compressionErrors)

    Mechanical.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-5, listNameDualVarOutput = dualNames, listNameDualVarGappyIndicesforECM = ["evrcum"])

    print("CompressOperator done")

    SIO.SaveState("collectionProblemData", collectionProblemData)
    SIO.SaveState("snapshotCorrelationOperator", snapshotCorrelationOperator)


    folderHandler.SwitchToExecutionFolder()

    assert np.max(compressionErrors) < 1.e-5, "!!! Regression detected !!! compressionErrors have become too large"


if __name__ == "__main__":

    from BasicTools.Helpers import Profiler as P
    p = P.Profiler()
    p.Start()

    test()

    p.Stop()
    print(p)