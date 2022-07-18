import sys
import feelpp
from Mordicus.Modules.Cemosis.IO import FeelppMeshReader as FMR
from Mordicus.Modules.Cemosis.IO import FeelppSolutionReader as FSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD
from Mordicus.Core.Helpers import FolderHandler as FH

def test():
    e = feelpp.Environment(sys.argv, config=feelpp.globalRepository("mordicus-pod"))

    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()
    
    folder = "computation1/"
    mesh_file_name = folder + "heat.mesh.msh"
    solution_file_name = folder + "temperature"
    dim = 2
    mesh_reader = FMR.FeelppMeshReader(mesh_file_name, dim)
    mesh = mesh_reader.ReadMesh()

    Xh = feelpp.functionSpace(mesh.GetInternalStorage(), "Pch", 1)
    solution_reader = FSR.FeelppSolutionReader(mesh.GetInternalStorage(), Xh)
    number_of_snapshots = 400
    
    solution = S.Solution("T", 1, mesh.GetNumberOfNodes(), True)
    for time in range(number_of_snapshots):
        T = solution_reader.ReadSnapshotComponent(f"{solution_file_name}_{time}.h5", time, True)
        solution.AddSnapshot(T, time)

    problemData = PD.ProblemData(folder)
    problemData.AddSolution(solution)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.DefineVariabilityAxes(('mu',), (float, ))
    collectionProblemData.DefineQuantity("T", "temperature", "K")
    collectionProblemData.AddProblemData(problemData, mu=0.)
    print(
        "A collectionProblemData with problemDatas "
        + str(collectionProblemData.GetProblemSampling())
        + " has been constructed"
    )
    
    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "T", 1.e-8)
    collectionProblemData.AddReducedOrderBasis("T", reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")
    solution_reader.WriteReducedOrderBasis("reducedbasis", None, reducedOrderBasis=collectionProblemData.reducedOrderBases, fieldName="T")

test()
