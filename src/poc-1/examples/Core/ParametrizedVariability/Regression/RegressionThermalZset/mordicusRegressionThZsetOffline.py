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
from Mordicus.Core.DataCompressors import SnapshotPOD
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Core.Helpers import FolderHandler as FH
import numpy as np


def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()


    mesh = ZMR.ReadMesh("cube.geof")
    numberOfNodes = mesh.GetNumberOfNodes()
    solutionName = "TP"
    nbeOfComponents = 1
    primality = True

    collectionProblemData = CPD.CollectionProblemData()

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddVariabilityAxis('config',
                                                str,
                                                description="dummy variability")


    collectionProblemData.DefineQuantity(solutionName, "Temperature", "Celsius")

    parameters = [[100.0, 1000.0], [90.0, 1100.0], [110.0, 900.0], [105.0, 1050.0]]

    for i in range(4):
        folder = "Computation" + str(i + 1) + "/"
        solutionFileName = folder + "cube.ut"
        solutionReader = ZSR.ZsetSolutionReader(solutionFileName=solutionFileName)

        outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

        solution = S.Solution(
            solutionName=solutionName,
            nbeOfComponents=nbeOfComponents,
            numberOfNodes=numberOfNodes,
            primality=primality,
        )

        problemData = PD.ProblemData(folder)
        problemData.AddSolution(solution)


        for t in outputTimeSequence:
            snapshot = solutionReader.ReadSnapshot(
                solution.GetSolutionName(), t, solution.GetPrimality()
            )
            solution.AddSnapshot(snapshot, t)
            problemData.AddParameter(np.array(parameters[i] + [t]), t)

        #collectionProblemData.AddProblemData(problemData, Text=parameters[i][0], Tint=parameters[i][1])
        collectionProblemData.AddProblemData(problemData, config=folder)


    print("Solutions have been read")

    ##################################################
    # OFFLINE
    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, solutionName, 1.e-2
    )
    collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    collectionProblemData.CompressSolutions("TP")
    print("The solution has been compressed")


    from sklearn.gaussian_process.kernels import WhiteKernel, RBF, ConstantKernel, Matern
    from sklearn.gaussian_process import GaussianProcessRegressor

    #kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(0.01, 10.0)) * RBF(length_scale_bounds=(1e-2, 1e2)) + WhiteKernel(noise_level_bounds=(1e-10, 1e0))
    kernel = ConstantKernel(constant_value=1.0, constant_value_bounds=(0.01, 10.0)) * Matern(length_scale=1., nu=2.5) + WhiteKernel(noise_level=1, noise_level_bounds=(1e-10, 1e0))

    regressors = {"TP":GaussianProcessRegressor(kernel=kernel)}

    paramGrids = {}
    paramGrids["TP"] = {'kernel__k1__k1__constant_value':[0.1, 1.], 'kernel__k1__k2__length_scale': [1., 3., 10.], 'kernel__k2__noise_level': [1., 2.]}

    Regression.CompressOperator(collectionProblemData, regressors, paramGrids)

    SIO.SaveState("collectionProblemData", collectionProblemData)



    ##################################################
    ## check accuracy compression
    ##################################################

    compressionErrors = []

    for _, problemData in collectionProblemData.GetProblemDatas().items():
        solution = problemData.GetSolution("TP")
        CompressedSolution = solution.GetCompressedSnapshots()
        for t in solution.GetTimeSequenceFromCompressedSnapshots():
            reconstructedCompressedSnapshot = np.dot(CompressedSolution[t], reducedOrderBasis)
            exactSolution = solution.GetSnapshotAtTime(t)
            norml2ExactSolution = np.linalg.norm(exactSolution)
            if norml2ExactSolution != 0:
                relError = np.linalg.norm(reconstructedCompressedSnapshot-exactSolution)/norml2ExactSolution
            else:
                relError = np.linalg.norm(reconstructedCompressedSnapshot-exactSolution)
            compressionErrors.append(relError)


    folderHandler.SwitchToExecutionFolder()

    assert np.max(compressionErrors) < 1.e-2, "!!! Regression detected !!! compressionErrors have become too large"



if __name__ == "__main__":
    test()
