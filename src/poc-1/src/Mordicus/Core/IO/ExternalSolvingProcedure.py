# coding: utf-8
import subprocess
import shlex

import os.path as osp
from string import Template

class ExternalSolvingProcedure(object):
    """
    This objects says how to call an external solver from Mordicus
    
    Attributes:
    -----------
    
    - solver_cfg (dict): dictionary of environment variables useful to the call procedure
    
    - solver_call_procedure_type (str): one of ("shell", "python"), tells what to execute the script with

    - call_script=call_script (str): launching script
    """


    def __init__(self, **kwargs):
        """
        Constructor
        """
        list_argnames = ["solver_cfg", "solver_call_procedure_type", "call_script", "python_preprocessing"]
        for name in list_argnames:
            if name in kwargs:
                setattr(self, name, kwargs[name])
    
    def execute(self, script):
        """
        Executes as_run as a script
        
        Arguments
        ---------
        script : str
            shell script to execute
        
        Returns
        -------
        int
            return code
        """
        if hasattr(self, "solver_cfg"):
            script = script.format(**self.solver_cfg)
        seq = shlex.split(script)
        ret = subprocess.run(seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(ret.stdout)
        return ret

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
        
