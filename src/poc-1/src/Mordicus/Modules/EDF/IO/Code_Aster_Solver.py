"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
import subprocess
import shlex
from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure

class Code_Aster_Solver(ExternalSolvingProcedure):
    """
    Informations to call Code_Aster
    """


    def __init__(self, **kwargs):
        """
        Constructor
        """
        return super(Code_Aster_Solver, self).__init__(**kwargs)
    
    def import_resolution_data(self, data):
        """
        Imports a Code_Aster database into folder and adds to the export file
        """
        pass
    
    def execute(self, script):
        """
        Executes as_run as a script
        """
        if hasattr(self, "solver_cfg"):
            script = script.format(**self.solver_cfg)
        seq = shlex.split(script)
        ret = subprocess.run(seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(ret.stdout)
        return ret