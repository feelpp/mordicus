# -*- coding: utf-8 -*-

import numpy as np
import os
import os.path as osp
from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import CollectionProblemData as CPD

from Mordicus.Core.IO.SolverDataset import SolverDataset
from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase

from Mordicus.Core.Containers.SolutionStructures.SolutionStructureBase import SolutionStructureBase

from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Modules.Safran.Containers.Loadings import Temperature as T


def test():

    solution = Solution.Solution("U", 2, 10, True)

    solution.AddSnapshot(np.ones(20), 0.0)
    solution.AddSnapshot(1.+np.ones(20), 1.0)

    solution.AddCompressedSnapshots(np.ones(2), 0.0)
    solution.AddCompressedSnapshots(1.+np.ones(2), 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    loading = T.Temperature("U", "set1")
    problemData.AddLoading(loading)

    reducedOrderBases = np.ones((2, 20))

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.defineVariabilityAxes(["mu1"],
                                                [float],
                                                quantities=[("name", "unit")],
                                                descriptions=["Parameter long description"])
    collectionProblemData.addVariabilityAxis("mu2",
                                             float,
                                             quantity=("name", "unit"),
                                             description="Parameter long description")
    collectionProblemData.defineQuantity("U", "velocity", "m/s")
    collectionProblemData.AddProblemData(problemData, mu1=0., mu2=0.)
    collectionProblemData.AddProblemData(problemData, mu1=0., mu2=0.)
    collectionProblemData.getNumberOfVariabilityAxes()
    collectionProblemData.GetProblemData(mu1=0., mu2=0.)
    collectionProblemData.GetProblemDatas()
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBases)
    collectionProblemData.GetReducedOrderBasis("U")
    collectionProblemData.GetReducedOrderBases()
    collectionProblemData.GetNumberOfProblemDatas()
    collectionProblemData.GetSolutionsNumberOfDofs("U")
    collectionProblemData.GetSolutionsNumberOfNodes("U")
    collectionProblemData.GetProblemSampling()
    collectionProblemData.GetGlobalNumberOfSnapshots("U")
    collectionProblemData.GetGlobalNumberOfSnapshots("U", skipFirst = True)
    collectionProblemData.GetSolutionTimeSteps("U")
    collectionProblemData.GetSolutionTimeSteps("U", skipFirst = True)
    collectionProblemData.GetSolutionsNumberOfComponents("U")
    collectionProblemData.GetSnapshots("U")
    collectionProblemData.GetCompressedSnapshots("U")
    collectionProblemData.GetSnapshots("U", skipFirst = True)
    collectionProblemData.GetCompressedSnapshots("U", skipFirst = True)
    collectionProblemData.GetCompressedSnapshots("U", skipFirst = True)
    collectionProblemData.GetSnapshotsAtTimes("U", np.array([0., 1.]))
    collectionProblemData.GetCompressedSnapshotsAtTimes("U", np.array([0., 1.]))
    collectionProblemData.GetLoadingsOfType("temperature")



    for s in collectionProblemData.SnapshotsIterator("U"):
        pass
    for s in collectionProblemData.SnapshotsIterator("U", skipFirst = True):
        pass
    for s in collectionProblemData.GetCompressedSnapshots("U"):
        pass
    for s in collectionProblemData.GetCompressedSnapshots("U", skipFirst = True):
        pass

    collectionProblemData.GetReducedOrderBasisNumberOfModes("U")
    collectionProblemData.SetDataCompressionData("toto", 1.)
    collectionProblemData.GetDataCompressionData("toto")

    projectedReducedOrderBasis = collectionProblemData.ComputeReducedOrderBasisProjection("U", np.ones((3, 20)))
    collectionProblemData.ConvertCompressedSnapshotReducedOrderBasis("U", projectedReducedOrderBasis)


    problemData.AddParameter(np.zeros(2), 0.0)
    collectionProblemData.GetParameterDimension()

    SIO.SaveState("temp", collectionProblemData)
    SIO.LoadState("temp")
    os.system("rm -rf temp.pkl")

    # Adding a dummy solver that does nothing
    call_script = """
bash "{input_root_folder}/{input_main_file}"
    """
    # Adding a dataset
    data_dir = osp.join(osp.dirname(osp.abspath(__file__)), osp.pardir, osp.pardir, "TestsData", "Core", "Containers")
    solver_cfg = {"solver_name" : "Foo"}
    solver = ExternalSolvingProcedure(solver_call_procedure_type="shell",
                                      solver_cfg=solver_cfg,
                                      call_script=call_script)
    input_data = {"input_root_folder" : data_dir,
                  "input_main_file"   : "generate_snapshots.sh",
                  "input_instruction_file" : "generate_snapshots.sh",
                  "input_mordicus_data": {},
                  "input_result_path" : "snapshot.npy",
                  "input_result_type" : "numpy_file"}
    dataset = SolverDataset(ProblemData.ProblemData, solver, input_data)
    collectionProblemData.SetTemplateDataset(dataset)

    class NumPySolutionReader(SolutionReaderBase):
        def __init__(self, fileName, timeIt):
            self.fileName = fileName # To make generic later on

        def ReadTimeSequenceFromSolutionFile(self, filename):
            return np.array([0.])

        def ReadSnapshotComponent(self, fieldName, time, primality, structure):
            return np.load(self.fileName)

    collectionProblemData.SetSolutionStructure("U", SolutionStructureBase(fixed=(20, 1)))
    solStruct = collectionProblemData.GetSolutionStructure("U")

    problemData = collectionProblemData.solve(mu1=0., mu2=1.,
                                              extract=("U", ),
                                              primalities={"U": True},
                                              solutionReaderType=NumPySolutionReader)
    collectionProblemData.SetReducedTemplateDataset(dataset)
    problemData = collectionProblemData.solve_reduced(mu1=0., mu2=1.,
                                                      extract=("U", ),
                                                      primalities={"U": True},
                                                      solutionReaderType=NumPySolutionReader)
    collectionProblemData.specificDatasets["computeAPosterioriError"] = dataset
    problemData = collectionProblemData.computeAPosterioriError(extract=("U", ),
                                                                primalities={"U": True},
                                                                solutionStructures={"U": solStruct},
                                                                solutionReaderType=NumPySolutionReader)
    # Define the support of varying parameters
    arr_mu1 = np.array([0. , 1.])
    arr_mu2 = np.array([0. , 1.])
    collectionProblemData.defineVariabilitySupport(["mu1", "mu2"],
                                                   [arr_mu1, arr_mu2])
    
    grid = collectionProblemData.generateVariabilitySupport()
    print(collectionProblemData)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
