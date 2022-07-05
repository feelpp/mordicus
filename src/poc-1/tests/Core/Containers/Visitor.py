# -*- coding: utf-8 -*-

import numpy as np
import os
import os.path as osp
import tempfile
import shutil

from Mordicus.Core.Containers import ProblemData
from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import CollectionProblemData as CPD

from Mordicus.Core.IO.SolverDataset import SolverDataset
from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase

from Mordicus.Core.Containers.SolutionStructures.SolutionStructureBase import SolutionStructureBase

from Mordicus.Modules.Safran.Containers.Loadings import Temperature as T

from Mordicus import GetTestDataPath


from Mordicus.Core.Containers.Visitor import (importFromJSON, exportToJSON, checkValidity)

def test_visitor(): 
    """test visitor for json deserialisation
    """    
    solution = Solution.Solution("U", 2, 10, True)

    solution.AddSnapshot(np.ones(20), 0.0)
    solution.AddSnapshot(1.+np.ones(20), 1.0)

    solution.AddCompressedSnapshots(np.ones(2), 0.0)
    solution.AddCompressedSnapshots(1.+np.ones(2), 1.0)

    problemData = ProblemData.ProblemData("computation1")
    problemData.AddSolution(solution)

    loading = T.Temperature("U", "set1")
    problemData.AddLoading(loading)


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
    reducedOrderBasisU = np.ones((2, 20))
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
    collectionProblemData.SetDataCompressionData("toto", 1.)
    collectionProblemData.SetOperatorCompressionData({"toto": np.array([1., 2.])})

    problemData.AddParameter(np.zeros(2), 0.0)

    collectionProblemData.CompressSolutions("U")
    
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
    solStruct = SolutionStructureBase(fixed=(20, 1))
    collectionProblemData.SetSolutionStructure("U", solStruct)
    collectionProblemData.SetReducedTemplateDataset(dataset)

    # Define the support of varying parameters
    arr_mu1 = np.array([0. , 1.])
    arr_mu2 = np.array([0. , 1.])
    collectionProblemData.DefineVariabilitySupport(["mu1", "mu2"],
                                                   [arr_mu1, arr_mu2])


    save_repo = tempfile.mkdtemp(suffix="Light", prefix="SaveMordicus")
    save_repo_full = tempfile.mkdtemp(suffix="Full", prefix="SaveMordicus")
    print(save_repo)
    try:
        exportToJSON(save_repo, collectionProblemData, reconstruct=False)
        exportToJSON(save_repo_full, collectionProblemData, reconstruct=True)
        assert checkValidity(osp.join(save_repo, "reducedModel.json")), "Produced json is not valid"
        assert checkValidity(osp.join(save_repo_full, "reducedModel.json")), "Produced full json is not valid"
    finally:
        # Comment these two lines in order to debug JSON file
        #shutil.rmtree(save_repo)
        #shutil.rmtree(save_repo_full)
        pass

    collectionProblemDataLight = importFromJSON(save_repo)
    collectionProblemDataFull = importFromJSON(save_repo_full, reconstruct=True)

    assert len(collectionProblemDataLight.quantityDefinition) == 1
    assert len(collectionProblemDataFull.quantityDefinition) == 1
    assert len(collectionProblemDataLight.variabilityDefinition) == 2
    assert len(collectionProblemDataFull.variabilityDefinition) == 2
    assert collectionProblemDataFull.GetReducedOrderBasisNumberOfModes("U") == 2
    assert len(collectionProblemDataLight.GetOperatorCompressionData()) == 1
    assert len(collectionProblemDataFull.GetOperatorCompressionData()) == 1
    np.testing.assert_almost_equal( collectionProblemDataFull.GetOperatorCompressionData()['toto'], collectionProblemData.GetOperatorCompressionData()['toto'])

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
