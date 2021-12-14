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

from Mordicus import GetTestDataPath


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

    reducedOrderBasisU = np.ones((2, 20))

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.DefineVariabilityAxes(["mu1"],
                                                [float],
                                                quantities=[("name", "unit")],
                                                descriptions=["Parameter long description"])
    collectionProblemData.AddVariabilityAxis("mu2",
                                             float,
                                             quantity=("name", "unit"),
                                             description="Parameter long description")
    collectionProblemData.DefineQuantity("U", "velocity", "m/s")
    collectionProblemData.AddProblemData(problemData, mu1=0., mu2=0.)
    collectionProblemData.AddProblemData(problemData, mu1=0., mu2=0.)
    assert collectionProblemData.GetNumberOfVariabilityAxes() == 2
    assert id(collectionProblemData.GetProblemData(mu1=0., mu2=0.)) == id(problemData)
    collectionProblemData.GetProblemDatas()
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
    assert id(collectionProblemData.GetReducedOrderBasis("U")) == id(reducedOrderBasisU)
    assert id(collectionProblemData.GetReducedOrderBases()["U"]) == id(reducedOrderBasisU)
    assert collectionProblemData.GetNumberOfProblemDatas() == 1
    assert collectionProblemData.GetSolutionsNumberOfDofs("U") == 20
    assert collectionProblemData.GetSolutionsNumberOfNodes("U") == 10
    assert collectionProblemData.GetProblemSampling() == [(0.0, 0.0)]
    assert collectionProblemData.GetGlobalNumberOfSnapshots("U") == 2
    assert collectionProblemData.GetGlobalNumberOfSnapshots("U", skipFirst = True) == 1
    assert collectionProblemData.GetSolutionTimeSteps("U")[0] == 0.
    assert collectionProblemData.GetSolutionTimeSteps("U", skipFirst = True) == [1.]
    assert collectionProblemData.GetSolutionsNumberOfComponents("U") == 2
    np.testing.assert_almost_equal(collectionProblemData.GetSnapshots("U"), [np.ones(20),2.*np.ones(20)])
    np.testing.assert_almost_equal(collectionProblemData.GetCompressedSnapshots("U"), [np.ones(2),2.*np.ones(2)])
    np.testing.assert_almost_equal(collectionProblemData.GetSnapshots("U", skipFirst = True), [2.*np.ones(20)])
    np.testing.assert_almost_equal(collectionProblemData.GetCompressedSnapshots("U", skipFirst = True), [2.*np.ones(2)])
    np.testing.assert_almost_equal(collectionProblemData.GetSnapshotsAtTimes("U", np.array([0., 1.])), [np.ones(20),2.*np.ones(20)])
    np.testing.assert_almost_equal(collectionProblemData.GetCompressedSnapshotsAtTimes("U", np.array([0., 1.])), [np.ones(2),2.*np.ones(2)])
    assert id(collectionProblemData.GetLoadingsOfType("temperature")[0]) == id(loading)


    for s in collectionProblemData.SnapshotsIterator("U"):
        pass
    for s in collectionProblemData.SnapshotsIterator("U", skipFirst = True):
        pass
    for s in collectionProblemData.GetCompressedSnapshots("U"):
        pass
    for s in collectionProblemData.GetCompressedSnapshots("U", skipFirst = True):
        pass

    assert collectionProblemData.GetReducedOrderBasisNumberOfModes("U") == 2
    collectionProblemData.SetDataCompressionData("toto", 1.)
    assert collectionProblemData.GetDataCompressionData("toto") == 1.

    projectedReducedOrderBasis = collectionProblemData.ComputeReducedOrderBasisProjection("U", np.ones((3, 20)))
    np.testing.assert_almost_equal(projectedReducedOrderBasis, 20.*np.ones((3, 2)))
    np.testing.assert_almost_equal(solution.GetCompressedSnapshotsList(), [[1., 1.], [2., 2.]])
    collectionProblemData.ConvertCompressedSnapshotReducedOrderBasis("U", projectedReducedOrderBasis)
    np.testing.assert_almost_equal(solution.GetCompressedSnapshotsList(), [[40., 40., 40.], [80., 80., 80.]])

    problemData.AddParameter(np.zeros(2), 0.0)
    assert collectionProblemData.GetParameterDimension() == 2

    SIO.SaveState("temp", collectionProblemData)
    SIO.LoadState("temp")
    os.system("rm -rf temp.pkl")

    # Adding a dummy solver that does nothing
    callScript = """
bash "{inputRootFolder}/{inputMainFile}"
    """
    # Adding a dataset
    #dataDir = osp.join(osp.dirname(osp.abspath(__file__)), osp.pardir, osp.pardir, "TestsData", "Core", "Containers")
    dataDir = osp.join(GetTestDataPath(), "Core", "Containers")
    solverCfg = {"solverName" : "Foo"}
    solver = ExternalSolvingProcedure(solverCallProcedureType="shell",
                                      solverCfg=solverCfg,
                                      callScript=callScript)
    input_data = {"inputRootFolder" : dataDir,
                  "inputMainFile"   : "generate_snapshots.sh",
                  "inputInstructionFile" : "generate_snapshots.sh",
                  "inputMordicusData": {},
                  "inputResultPath" : "snapshot.npy",
                  "inputResultType" : "numpyFile"}
    dataset = SolverDataset(ProblemData.ProblemData, solver, input_data)
    collectionProblemData.SetTemplateDataset(dataset)

    class NumPySolutionReader(SolutionReaderBase):
        def __init__(self, fileName, timeIt):
            self.fileName = fileName # To make generic later on

        def ReadTimeSequenceFromSolutionFile(self, filename):
            return np.array([0.])

        def ReadSnapshotComponent(self, fieldName, time, primality, structure):
            return np.load(self.fileName)

    solStruct = SolutionStructureBase(fixed=(20, 1))
    collectionProblemData.SetSolutionStructure("U", solStruct)
    assert id(collectionProblemData.GetSolutionStructure("U")) == id(solStruct)

    problemData = collectionProblemData.Solve(mu1=0., mu2=1.,
                                              extract=("U", ),
                                              primalities={"U": True},
                                              solutionReaderType=NumPySolutionReader)
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetSnapshotAtTime(0.), np.arange(20))
    collectionProblemData.SetReducedTemplateDataset(dataset)
    problemData = collectionProblemData.SolveReduced(mu1=0., mu2=1.,
                                                      extract=("U", ),
                                                      primalities={"U": True},
                                                      solutionReaderType=NumPySolutionReader)
    assert bool(problemData[0].GetSolution("U").GetCompressedSnapshots()) == False
    collectionProblemData.specificDatasets["computeAPosterioriError"] = dataset
    problemData = collectionProblemData.ComputeAPosterioriError(extract=("U", ),
                                                                primalities={"U": True},
                                                                solutionStructures={"U": solStruct},
                                                                solutionReaderType=NumPySolutionReader)
    assert bool(problemData.GetSolution("U").GetCompressedSnapshots()) == False

    os.system("rm -r "+osp.join(GetTestDataPath(), "Core", "runFull_mu1_0.000e+00_mu2_1.000e+00"))
    os.system("rm -r "+osp.join(GetTestDataPath(), "Core", "runReduced_mu1_0.000e+00_mu2_1.000e+00"))
    os.system("rm -r "+dataDir+os.sep+"snapshot.npy")
    os.system("rm -r "+dataDir+os.sep+"generate_snapshots.py")

    # Define the support of varying parameters
    arr_mu1 = np.array([0. , 1.])
    arr_mu2 = np.array([0. , 1.])
    collectionProblemData.DefineVariabilitySupport(["mu1", "mu2"],
                                                   [arr_mu1, arr_mu2])

    grid = collectionProblemData.GenerateVariabilitySupport()
    np.testing.assert_almost_equal(grid, [[0., 0.],[0., 1.],[1., 0.],[1., 1.]])

    print(collectionProblemData)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
