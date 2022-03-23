# coding: utf-8
import os.path as osp
import os
import numpy as np
from Mordicus import GetTestDataPath
from Mordicus.Core.Containers.ResolutionData.ResolutionDataBase import ResolutionDataBase
from Mordicus.Core.Containers.FixedData.FixedDataBase import FixedDataBase

from Mordicus.Core.IO.SolverDataset import SolverDataset
from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure
from Mordicus.Core.Containers.ProblemData import ProblemData

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase

from Mordicus.Core.Containers.SolutionStructures.SolutionStructureBase import SolutionStructureBase


def test():
    # Doing a template dataset calling a file
    # Adding a dummy solver that does nothing
    callScript = """
{solverInstall} "{inputRootFolder}/{inputMainFile}"
    """
    # Adding a dataset
    dataDir = osp.join(GetTestDataPath(), "Core", "IO")
    solverCfg = {"solverInstall" : "/bin/bash"}
    def PythonPreprocessing(dataset):
        return
    solver = ExternalSolvingProcedure(solverCallProcedureType="shell",
                                      solverCfg=solverCfg,
                                      callScript=callScript,
                                      PythonPreprocessing=PythonPreprocessing)
    inputData = {"inputRootFolder"        : dataDir,
                  "inputMainFile"          : "inputMainFile.sh",
                  "inputInstructionFile"   : "inputInstructionFile",
                  "inputMordicusData"      : {"mordicusNpyData": "inputInstructionFile"},
                  "inputResultPath"        : "snapshot.npy",
                  "inputResultType"        : "numpyFile"}
    datasetTemplate = SolverDataset(ProblemData, solver, inputData)
    datasetInstance = datasetTemplate.Instantiate(mu1="0.0", mu2=0.0)

    class NumpySolutionReader(SolutionReaderBase):
        def __init__(self, fileName, timeIt):
            self.fileName = fileName # To make generic later on

        def ReadTimeSequenceFromSolutionFile(self, filename):
            return np.array([0.])

        def ReadSnapshotComponent(self, fieldName, time, primality, structure):
            return np.load(self.fileName)

    # extractResult is called by Run
    datasetInstance.Run(extract=("U", ),
                         primalities={"U": True},
                         solutionStructures={"U": SolutionStructureBase(fixed=(20, 1))},
                         solutionReaderType=NumpySolutionReader)

    # Now, call extractResult for other types of results for coverage, that is FixedDataBase and ResolutionDataBase
    inputData = {"inputRootFolder"        : dataDir,
                  "inputMainFile"          : "inputMainFileResolution.sh",
                  "inputInstructionFile"   : "inputInstructionFileResolution.py",
                  "inputMordicusData"      : {"mordicusNpyData": "inputInstructionFileResolution.py"},
                  "inputResultPath"        : "snapshot.npy",
                  "inputResultType"        : "matrix"}
    dataset = SolverDataset(ResolutionDataBase, solver, inputData)
    resolutionData = dataset.Run()
    nparray = resolutionData.GetInternalStorage()
    np.testing.assert_almost_equal(nparray, np.arange(20))

    inputData = {"inputRootFolder"        : dataDir,
                  "inputMainFile"          : "inputMainFileResolution.sh",
                  "inputInstructionFile"   : "inputInstructionFileResolution.py",
                  "inputMordicusData"      : {"mordicusNpyData": "inputInstructionFileResolution.py"},
                  "inputResultPath"        : "snapshot.npy",
                  "inputResultType"        : "file"}
    dataset = SolverDataset(FixedDataBase, solver, inputData)
    fixedData = dataset.Run()
    fixedData.GetInternalStorage()

    print(dataset)

    os.system("rm -r "+osp.join(GetTestDataPath(), "Core", "runFull_mu1_0.0_mu2_0.000e+00"))
    os.system("rm -r "+osp.join(GetTestDataPath(), "Core", "IO", "snapshot.npy"))

    print("ok")


if __name__ == "__main__":
    print(test())  # pragma: no cover
