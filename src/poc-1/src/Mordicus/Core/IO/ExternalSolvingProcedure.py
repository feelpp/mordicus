# coding: utf-8

import subprocess
import shlex

import os.path as osp
from string import Template

class ExternalSolvingProcedure(object):
    """
    This objects says how to call an external solver from Mordicus

    Attributes
    ----------
    solverCfg : dict
        dictionary of environment variables useful to the call procedure
    solverCallProcedureType : str
        one of ("shell", "python"), tells what to execute the script with
    callScript : str
        launching script
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """
        list_argnames = ["solverCfg", "solverCallProcedureType", "callScript", "PythonPreprocessing"]
        for name in list_argnames:
            if name in kwargs:
                setattr(self, name, kwargs[name])

    def Execute(self, script):
        """
        Executes as_run as a script

        Parameters
        ----------
        script : str
            shell script to execute

        Returns
        -------
        int
            return code
        """
        if hasattr(self, "solverCfg"):
            script = script.format(**self.solverCfg)
        seq = shlex.split(script)
        ret = subprocess.run(seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(ret.stdout)
        return ret

    def importMordicusData(self, inputData):
        """
        Sets input files from mordicus into launch procedure

        Parameters
        ----------
        inputData: dict
            dictionary with str as key (used as key to substitute in template of inputMainFile and input_instruction_file)
            and str as values (value to substitute with)
        """
        mordicusData = inputData.pop("input_mordicusData", {})
        inputInstructionFilePath = osp.join(inputData["inputRootFolder"], inputData["inputMainFile"])
        with open(inputInstructionFilePath, "r") as f:
            mystr = f.read()
            mytemplate = Template(mystr)
            kws = {k: str(v) for k,v in mordicusData.items()}
            myinstance = mytemplate.safe_substitute(**kws)
        with open(inputInstructionFilePath, "w") as f:
            f.write(myinstance)


    def __str__(self):
        res = "ExternalSolvingProcedure\n"
        res += "solverCfg               : " + str(self.solverCfg) + "\n"
        res += "solverCallProcedureType : " + str(self.solverCallProcedureType) + "\n"
        res += "callScript              : " + str(self.callScript)
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

