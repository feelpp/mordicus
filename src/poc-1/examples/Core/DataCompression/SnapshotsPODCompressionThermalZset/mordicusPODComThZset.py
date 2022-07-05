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
from Mordicus.Core.DataCompressors import SnapshotPOD
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

    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

    solution = S.Solution("TP", 1, mesh.GetNumberOfNodes(), primality = True)
    for time in outputTimeSequence:
        TP = solutionReader.ReadSnapshot("TP", time, 1, primality=True)
        solution.AddSnapshot(TP, time)

    problemData = PD.ProblemData(folder)

    problemData.AddSolution(solution)


    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.DefineVariabilityAxes(('mu',), (float, ))
    collectionProblemData.DefineQuantity("TP", "temperature", "K")
    collectionProblemData.AddProblemData(problemData, mu=0.)
    print(
        "A collectionProblemData with problemDatas "
        + str(collectionProblemData.GetProblemSampling())
        + " has been constructed"
    )

    # loading = ZR.ReadLoading(folder+"cube.inp")


    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 1)

    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "TP", 1.e-8, l2ScalarProducMatrix
    )
    collectionProblemData.AddReducedOrderBasis("TP", reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    collectionProblemData.CompressSolutions("TP", l2ScalarProducMatrix)

    print("The solution has been compressed")

    from Mordicus.Modules.Safran.IO import PXDMFWriter as PW

    compressedSolution = solution.GetCompressedSnapshots()

    PW.WriteCompressedSolution(mesh, compressedSolution, reducedOrderBasis, "U")

    print("The compressed solution has been written in PXDMF Format")


    ##################################################
    ## check accuracy compression
    ##################################################


    compressionErrors = []

    for t in outputTimeSequence:

        reconstructedCompressedSolution = np.dot(compressedSolution[t], reducedOrderBasis)
        exactSolution = solution.GetSnapshot(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
        compressionErrors.append(relError)


    folderHandler.SwitchToExecutionFolder()

    assert np.max(compressionErrors) < 1.e-6, "!!! Regression detected !!! compressionErrors have become too large"


if __name__ == "__main__":
    test()
