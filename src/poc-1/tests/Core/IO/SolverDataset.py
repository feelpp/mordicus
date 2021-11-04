# coding: utf-8
import os.path as osp
import numpy as np
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
    call_script = """
echo "Calling a bash script that will emulate generation of the snapshot \n"

${solver_install} ${input_main_file}
    """
    # Adding a dataset
    data_dir = osp.join(osp.dirname(osp.abspath(__file__)), "data")
    solver_cfg = {"solver_install" : "/bin/bash"}
    solver = ExternalSolvingProcedure(solver_call_procedure_type="shell",
                                      solver_cfg=solver_cfg,
                                      call_script=call_script)
    input_data = {"input_root_folder"        : data_dir,
                  "input_main_file"          : "input_main_file.sh",
                  "input_instruction_file"   : "input_instruction_file",
                  "input_mordicus_data"      : {"mordicus_npy_data": "input_instruction_file"},
                  "input_result_path"        : "snapshot.npy",
                  "input_result_type"        : "numpy_file"}
    dataset = SolverDataset(ProblemData, solver, input_data)

    dataset.instantiate(mu1=0.0, mu2=0.0)

    class NumPySolutionReader(SolutionReaderBase):
        def __init__(self, fileName, timeIt):
            self.fileName = fileName # To make generic later on

        def ReadTimeSequenceFromSolutionFile(self, filename):
            return np.array([0.])

        def ReadSnapshotComponent(self, fieldName, time, primality, structure):
            return np.load(self.fileName)

    # extract_result is called by run
    dataset.run(extract=("U", ),
                primalities={"U": True},
                solutionStructures={"U": SolutionStructureBase(fixed=(20, 1))},
                solutionReaderType=NumPySolutionReader)

    # Now, call extract_result for other types of results for coverage, that is FixedDataBase and ResolutionDataBase
    input_data = {"input_root_folder"        : data_dir,
                  "input_main_file"          : "input_main_file.sh",
                  "input_instruction_file"   : "input_instruction_file_resolution.py",
                  "input_mordicus_data"      : {"mordicus_npy_data": "input_instruction_file_resolution.py"},
                  "input_result_path"        : "snapshot.npy",
                  "input_result_type"        : "matrix"}
    dataset = SolverDataset(ResolutionDataBase, solver, input_data)
    resolution_data = dataset.run()
    nparray = resolution_data.GetInternalStorage()

    input_data = {"input_root_folder"        : data_dir,
                  "input_main_file"          : "input_main_file.sh",
                  "input_instruction_file"   : "input_instruction_file_resolution.py",
                  "input_mordicus_data"      : {"mordicus_npy_data": "input_instruction_file_resolution.py"},
                  "input_result_path"        : "snapshot.npy",
                  "input_result_type"        : "file"}
    dataset = SolverDataset(FixedDataBase, solver, input_data)
    fixed_data = dataset.run()
    filepath = fixed_data.GetInternalStorage()

    print("ok")


if __name__ == "__main__":
    print(test())  # pragma: no cover
