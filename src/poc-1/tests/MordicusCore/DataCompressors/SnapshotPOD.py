# -*- coding: utf-8 -*-
import numpy as np
from BasicTools.Containers.UnstructuredMeshTools import CreateCube
from MordicusModules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from MordicusCore.Containers import ProblemData
from MordicusCore.Containers import CollectionProblemData
from MordicusCore.Containers import Solution
from MordicusCore.DataCompressors import SnapshotPOD


def test():
    
    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[3,4,3],spacing=[2.,2.,2.],ofTetras=True))
    mesh.GetDimensionality()
    
    nbeOfComponents = 3
    
    solution = Solution.Solution("U", nbeOfComponents, mesh.GetNumberOfNodes(), True)
    snapshot = np.ones(nbeOfComponents*mesh.GetNumberOfNodes())
    snapshot2 = np.ones(nbeOfComponents*mesh.GetNumberOfNodes())
    solution.AddSnapshot(0., snapshot)
    solution.AddSnapshot(1., snapshot2)
    
    problemData = ProblemData.ProblemData()
    problemData.AddSolution(solution)
    
    collectionProblemData = CollectionProblemData.CollectionProblemData()
    collectionProblemData.AddProblemData("computation1", problemData)
    
    reducedOrdrBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-8)
    collectionProblemData.AddReducedOrderBasis("U", reducedOrdrBasis)
    SnapshotPOD.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")
    
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
