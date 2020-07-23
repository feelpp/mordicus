from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Mines.IO.ZsetReader import ZsetMeshReader
from Mordicus.Modules.Mines.OperatorCompressors import HyperReduction as hrom
from Mordicus.Core.IO import StateIO as SIO

import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)


    folder = "MecaSequential/"

    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"

    meshReader = ZsetMeshReader(meshFileName)
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)


    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")



    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = mesh.GetNumberOfIntegrationPoint()
    nbeOfComponentsPrimal = 3
    nbeOfComponentsDual = 6


    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()


    solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)
    solutionEvcum = S.Solution("evcum", 1, numberOfIntegrationPoints, primality = False)

    for time in outputTimeSequence:
        U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
        solutionU.AddSnapshot(U, time)
        sigma = solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False)
        solutionSigma.AddSnapshot(sigma, time)
        evcum = solutionReader.ReadSnapshot("evrcum", time, 1, primality=False)
        solutionEvcum.AddSnapshot(evcum, time)



    problemData = PD.ProblemData(folder)
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionSigma)
    problemData.AddSolution(solutionEvcum)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.addVariabilityAxis("config", str)
    collectionProblemData.defineQuantity("U", "displacement", "m")
    collectionProblemData.defineQuantity("sigma", "Cauchy stress", "Pa")
    collectionProblemData.defineQuantity("evcum", "Cumulated plastic strain", "none")


    collectionProblemData.AddProblemData(problemData, config="case-1")

    #collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)

    reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(
            collectionProblemData, "U", 1.e-4
    )

    reducedOrderBasisSig = SP.ComputeReducedOrderBasisFromCollectionProblemData(
            collectionProblemData, "sigma", 1.e-4
    )

    reducedOrderBasisEvcum = SP.ComputeReducedOrderBasisFromCollectionProblemData(
            collectionProblemData, "evcum", 1.e-4
    )


    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
    collectionProblemData.AddReducedOrderBasis("sigma", reducedOrderBasisSig)
    collectionProblemData.AddReducedOrderBasis("evcum", reducedOrderBasisEvcum)

    ##SP.CompressSolutions( "U")
    collectionProblemData.CompressSolutions("U")


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


    hrom.BuildReducedIntegrationOperator( collectionProblemData, mesh, 1, listNameDualVarOutput=["sigma", "evcum"])

    print("CompressMecaOperator done")

    SIO.SaveState("collectionProblemData", collectionProblemData)

    os.chdir(initFolder)

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
