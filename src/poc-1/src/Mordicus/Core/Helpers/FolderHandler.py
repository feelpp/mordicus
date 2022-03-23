 # -*- coding: utf-8 -*-
from pathlib import Path
import os


class FolderHandler(object):
    """
    Class containing on object for switching between two folders:
    the one from which the script is launched and the one containing the script.

    Attributes
    ----------
    scriptFolder : str
        address of the folder containing the executed script
    executionFolder : str
        address of the folder from which the script is executed
    """

    def __init__(self, scriptAddress):
        """
        Parameters
        ----------
        scriptAddress : str
            absolute address of the script (file name included) being executed
        """
        self.scriptFolder = os.path.abspath(str(Path(scriptAddress).parents[0]))
        self.executionFolder = os.getcwd()


    def SwitchToScriptFolder(self):
        """
        Changes working directory to self.scriptFolder
        """
        os.chdir(self.scriptFolder)


    def SwitchToExecutionFolder(self):
        """
        Changes working directory to self.executionFolder
        """
        os.chdir(self.executionFolder)



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


