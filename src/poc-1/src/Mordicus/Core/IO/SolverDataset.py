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
        
        Arguments
        """
        self.produced_object = produced_object
        self.solver = solver
        self.input_data = input_data
        
    def run(self, **kwargs):
        """
        Executes the dataset with its solver
        """
        if "input_mordicus_data" in self.input_data:
            self.solver.import_mordicus_data(self.input_data)
        script_after_substitutions = self.solver.call_script.format(**self.input_data, **self.solver.solver_cfg)
        if hasattr(self.solver, "python_preprocessing"):
            self.solver.python_preprocessing(self)
        self.solver.execute(script_after_substitutions)
        return self.extract_result(**kwargs)
    
    def extract_result(self, extract=None, solutionStructures=None, primalities=None, solutionReaderType=None):
        """
        Calls constructor of object to import the file into a data structure
        
        Arguments
        ---------
        extract : tuple(str)
            identifier of the solutions to extract (e.g. "U", "sigma"...)
        solutionStructures: dict
            dict with solution name as key and solutionStructure as argument
        primalities: dict
            dict with solution name as key and solutionStructure as argument
        solutionReaderType : type
            specific solution reader to use
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
            
            if extract is None or solutionStructures is None or primalities is None:
                raise ValueError("To extract a ProblemData, all optional arguments to extract_result shall be present")
            # to be changed with the new syntax for defining parameters
            problemData = ProblemData("dummy")

            # create reader and get time sequence
            solutionReader = solutionReaderType(result_file_path, 0.0)
            outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile(extract[0])
            
            # loop over field to extract
            for field_name in extract:
            
                # primal field
                solutionStructure = solutionStructures[field_name]
                nbeOfComponents = solutionStructure.GetNumberOfComponents()
                numberOfNodes = solutionStructure.GetNumberOfNodes()
                primality = primalities[field_name]
            
                solution = Solution(field_name, nbeOfComponents, numberOfNodes, primality=primality)
                
                # Read the solutions from file
                for time in outputTimeSequence:
                    snap = solutionReader.ReadSnapshotComponent(field_name, time, primality, solutionStructure)
                    solution.AddSnapshot(snap, time)
                    
                problemData.AddSolution(solution)
            
            return problemData

        return obj
    
        # typical code to read the solution on one parameter value

    def instantiate(self, **kwargs):
        """
        Instantiate a template dataset. Replace parameters in file by their values
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
            myinstance = mytemplate.safe_substitute(**kws)
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
        # tmp to emule
        shutil.copyfile(osp.join(self.input_data["input_root_folder"], self.input_data["input_result_path"]), 
                        osp.join(dirname, basestr + ".rmed"))        
        # end tmp to emule
        input_data = {"input_root_folder"      : dirname,
                      "input_main_file"        : basestr + ".export",
                      "input_instruction_file" : basestr + ".comm",
                      "input_mordicus_data"    : self.input_data["input_mordicus_data"],
                      "input_result_path"      : basestr + ".rmed",
                      "input_result_type"      : "med_file"}

        return SolverDataset(self.produced_object,
                             self.solver,
                             input_data)
        
    def accept(self, visitor, cpd):
        """
        Accept visitor
        """
        return visitor.visitDataSet(self, cpd)
