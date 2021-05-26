# -*- coding: utf-8 -*-
import numpy as np

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
import os


class VTKSolutionReader(SolutionReaderBase):
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


    def __init__(self, SolutionName):
        self.SolutionName = SolutionName        


    def VTKReadToNp(self, FileName): #.vtu
        from BasicTools.IO.VtuReader import LoadVtuWithVTK
        from vtk.numpy_interface import dataset_adapter as dsa

        data = LoadVtuWithVTK(FileName)
        #print(data)
        npArray = dsa.WrapDataObject(data).GetPointData().GetArray(self.SolutionName)
      
        return npArray

