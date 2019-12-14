# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.OperatorCompressors import Mechanics as Meca
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import CollectionProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Core import GetTestDataPath
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.FE import FETools as FT


def test():
    
    
    folder = GetTestDataPath() + "Zset/"
    
    mesh = ZMR.ReadMesh(folder + "cube.geof")
    
    solutionFileName = folder + "cube.ut"
    reader = ZSR.ZsetSolutionReader(solutionFileName)
    
    
    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    nbeOfComponentsPrimal = mesh.GetDimensionality()
    nbeOfComponentsDual = 6
    
    print("numberOfNodes =", numberOfNodes)
    print("numberOfIntegrationPoints =", numberOfIntegrationPoints)
    
    outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()
    

    solutionU = Solution.Solution("U", nbeOfComponentsPrimal, numberOfNodes, True)
    solutionSigma = Solution.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, False)
    
    
    for t in outputTimeSequence:
        
        U1 = reader.ReadSnapshot("U1", t, primality=True)
        U2 = reader.ReadSnapshot("U2", t, primality=True)
        U3 = reader.ReadSnapshot("U3", t, primality=True)
        solutionU.AddSnapshot(t, np.concatenate([U1, U2, U3]))
        
        sig11 = reader.ReadSnapshot("sig11", t, primality=False)
        sig22 = reader.ReadSnapshot("sig22", t, primality=False)
        sig33 = reader.ReadSnapshot("sig33", t, primality=False)
        sig12 = reader.ReadSnapshot("sig12", t, primality=False)
        sig23 = reader.ReadSnapshot("sig23", t, primality=False)
        sig31 = reader.ReadSnapshot("sig31", t, primality=False)
        solutionSigma.AddSnapshot(t, np.concatenate([sig11, sig22, sig33, sig12, sig23, sig31]))

    
    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionSigma)

    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)
    
    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)
    
    reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "U", 1.e-3
    )
    reducedOrderBasisSigma = SP.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, "sigma", 1.e-3
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
    collectionProblemData.AddReducedOrderBasis("sigma", reducedOrderBasisSigma)


    operatorCompressionData = Meca.CompressMecaOperator(
        collectionProblemData, mesh, 1.e-3
    )

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
