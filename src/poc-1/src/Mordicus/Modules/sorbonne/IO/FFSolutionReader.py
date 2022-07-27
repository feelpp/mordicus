# -*- coding: utf-8 -*-
import numpy as np
import subprocess
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
import os
import os.path as osp

class FFSolutionReader(SolutionReaderBase):
    """
    Class containing a reader for VTK data strucure

    Attributes
    ----------
    solutionName : str
        name of the filed of the solution
    tmpbaseFile : str
        base name of the solution file
    nec_i : int
        counter to add to tmpbaseFile
    """


    def __init__(self, SolutionName,mesh):
        self.SolutionName = SolutionName
        self.mesh=mesh
        

    def FFReadToNp(self, externalFolder,FileName): #.txt
       
        currentFolder=os.getcwd()
        
        try:
            FNULL=open(os.devnull,'w')
            ret=subprocess.run(["FreeFem++-nw " + externalFolder+"/FFtoVTK.edp -mesh "+ self.mesh +" -file "+ FileName +" -fieldName "+self.SolutionName],stdout=FNULL, stderr=subprocess.PIPE,shell=True)
                        
            ret.check_returncode()
        except subprocess.CalledProcessError:
            retstr="Error File convertion FreeFem to VTK \n" + "    Returns error:\n" + str(ret.stderr)
            raise OSError(ret.returncode,retstr)


