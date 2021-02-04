"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
import os
import os.path as osp
import shutil
import numpy as np

from Mordicus.Core.Containers.FixedData.FixedDataBase import FixedDataBase
from Mordicus.Core.Containers.ResolutionData.ResolutionDataBase import ResolutionDataBase
from Mordicus.Core.Containers.ProblemData import ProblemData
from Mordicus.Core.Containers.Solution import Solution

from Mordicus.Modules.EDF.IO.MEDSolutionReader import MEDSolutionReader


class SolverDataset(object):
    """
    Gathers all data to be provided to a *SolvingProcedure*
    
    Attributes:
    -----------
    
    - produced_object (cls) : class of produced python object (after callback is called)
    
    - solver (SolvingProcedure) : solver object associated with the dataset
    
    - input data (dict) : dictionary of all parameters to be passed to the calling procedure 
    """


    def __init__(self, produced_object, solver, input_data):
        """
        Constructor
        """
        self.produced_object = produced_object
        self.solver = solver
        self.input_data = input_data
        
    def run(self, **kwargs):
        """
        Executes the dataset with its solver
        """
        if "input_resolution_data" in self.input_data:
            self.solver.import_resolution_data(self.input_data.pop("input_resolution_data"))
        script_after_substitutions = self.solver.call_script.format(**self.input_data, **self.solver.solver_cfg)
        if hasattr(self.solver, "python_preprocessing"):
            self.solver.python_preprocessing(self)
        self.solver.execute(script_after_substitutions)
        return self.extract_result(**kwargs)
    
    def extract_result(self, **kwargs):
        """
        Calls constructor of object to import the file into a data structure
        """
        result_file_path = osp.join(self.input_data["input_root_folder"], self.input_data["input_result_path"])
        if self.produced_object == FixedDataBase:
            obj = self.produced_object()
            obj.SetInternalStorage(result_file_path)
        if self.produced_object == ResolutionDataBase:
            obj = self.produced_object()
            if self.input_data["input_result_type"] == "matrix":
                obj.SetInternalStorage(np.load(result_file_path))
        if self.produced_object == ProblemData:
            # create reader and get time sequence
            solutionReader = MEDSolutionReader(result_file_path)
            outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile("U")
            
            # primal field
            sampleFieldPrimal = kwargs["sampleFieldPrimal"]
            nbeOfComponentsPrimal = sampleFieldPrimal.getNumberOfComponents()
            numberOfNodes = sampleFieldPrimal.getNumberOfTuples()
            
            solutionU = Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
            
            # dual field
            sampleFieldDual = kwargs["sampleFieldDual"]
            nbeOfComponentsDual = sampleFieldDual.getNumberOfComponents()
            numberOfIntegrationPoints = sampleFieldDual.getNumberOfTuples()
            
            print("nbeOfComponentsDual = ", nbeOfComponentsDual)
            print("numberOfIntegrationPoints = ", numberOfIntegrationPoints)
            solutionSigma = Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)
            
            # Read the solutions from file
            for time in outputTimeSequence:
                U = solutionReader.ReadSnapshotComponent("U", time, primality=True)

                solutionU.AddSnapshot(U, time)
                sigma = solutionReader.ReadSnapshotComponent("sigma", time, primality=False)
                solutionSigma.AddSnapshot(sigma, time)
            
            # to be changed with the new syntax for defining parameters
            problemData = ProblemData("dummy")
            problemData.AddSolution(solutionU)
            problemData.AddSolution(solutionSigma)
            return problemData

        return obj
    
        # typical code to read the solution on one parameter value

    def instantiate(self, **kwargs):
        """Instantiate a template dataset. Replace parameters in file by their values
        """
        if "reduced" in kwargs and kwargs.pop("reduced"):
            basestr = "reduced"
        else:
            basestr = "template"
        from string import Template
        with open(osp.join(self.input_data["input_root_folder"], self.input_data["input_instruction_file"]), "r") as f:
            mystr = f.read()
            mytemplate = Template(mystr)
            kws = {k: str(v) for k,v in kwargs.items()}
            myinstance = mytemplate.substitute(**kws)
        dirbname = basestr + "_".join([str(hash(v)) for v in kws.values()])
        dirname = osp.join(osp.dirname(self.input_data["input_root_folder"]), dirbname)
        if osp.exists(dirname):
            shutil.rmtree(dirname)
        # Create file in directory name
        os.makedirs(dirname, exist_ok=False)
        with open(osp.join(dirname, basestr + ".comm"), "w") as f:
            f.write(myinstance)
        shutil.copyfile(osp.join(self.input_data["input_root_folder"], self.input_data["input_main_file"]), 
                        osp.join(dirname, basestr + ".export"))
        input_data = {"input_root_folder"      : dirname,
                      "input_main_file"        : basestr + ".export",
                      "input_instruction_file" : basestr + ".comm",
                      "input_resolution_data"  : self.input_data.get("input_root_folder"),
                      "input_result_path"      : basestr + ".rmed",
                      "input_result_type"      : "med_file"}

        return SolverDataset(self.produced_object,
                             self.solver,
                             input_data)