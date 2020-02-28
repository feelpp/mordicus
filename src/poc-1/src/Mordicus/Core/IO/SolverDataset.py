"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""

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
        
    def run(self):
        """
        Executes the dataset with its solver
        """
        if "input_resolution_data" in self.input_data:
            self.solver.import_resolution_data(self.input_data.pop("input_resolution_data"))
        script_after_substitutions = self.sover.call_script.format(**self.input_data)
        self.solver.execute(script_after_substitutions)
        