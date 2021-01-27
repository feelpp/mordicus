# coding: utf-8

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