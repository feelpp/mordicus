"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
import os.path as osp
from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure
from string import Template

class Code_Aster_Solver(ExternalSolvingProcedure):
    """
    Informations to call Code_Aster
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """
        return super(Code_Aster_Solver, self).__init__(**kwargs)

    def import_mordicus_data(self, input_data):
        """
        Sets input files from mordicus into launch procedure
        
        mordicusData: dict
            dictionary with str as key (used as key to substitute in template of input_main_file and input_instruction_file)
            and str as values (value to substitute with)
        """
        mordicus_data = input_data.pop("input_mordicus_data", {})
        input_instruction_file_path = osp.join(input_data["input_root_folder"], input_data["input_main_file"])
        with open(input_instruction_file_path, "r") as f:
            mystr = f.read()
            mytemplate = Template(mystr)
            kws = {k: str(v) for k,v in mordicus_data.items()}
            myinstance = mytemplate.safe_substitute(**kws)
        with open(input_instruction_file_path, "w") as f:
            f.write(myinstance)