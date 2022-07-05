# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

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


def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()


    folder = "Computation1/"

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


    solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
    solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)

    for time in outputTimeSequence:
        U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
        solutionU.AddSnapshot(U, time)
        sigma = solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False)
        solutionSigma.AddSnapshot(sigma, time)


    problemData = PD.ProblemData(folder)
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionSigma)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis('config',
                                             str,
                                             description="dummy variability")
    collectionProblemData.DefineQuantity("U", "displacement", "m")
    collectionProblemData.DefineQuantity("sigma", "stress", "Pa")
    collectionProblemData.AddProblemData(problemData, config="case-1")


    print("ComputeL2ScalarProducMatrix...")
    snapshotCorrelationOperator = {}
    snapshotCorrelationOperator["U"] = FT.ComputeL2ScalarProducMatrix(mesh, 3)

    SP.CompressData(collectionProblemData, "U", 1.e-6, snapshotCorrelationOperator["U"])
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

    Mechanical.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-6)

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