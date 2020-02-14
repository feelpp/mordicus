# -*- coding: utf-8 -*-
import numpy as np

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
import os


primalSolutionComponents = {1:[""], 2:["1", "2"], 3:["1", "2", "3"]}


class VTKSolutionReader(SolutionReaderBase):
    """
    Class containing a reader for VTK data strucure

    Attributes
    ----------
    solutionFileName : str
        name of the VTK data structure with solutions (.vtu)
    """

    def __init__(self, solutionFileName):
        """
        Parameters
        ----------
        solutionFileName : str, optional
        """
        super(VTKSolutionReader, self).__init__()

        assert isinstance(solutionFileName, str)
        
        if type(solutionFileName) == str: 
           folder = str(Path(solutionFileName).parents[0])
           suffix = str(Path(solutionFileName).suffix)
           stem = str(Path(solutionFileName).stem)
           
           if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover 
               self.solutionFileName = folder + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
           else:
               self.solutionFileName = solutionFileName        

        

    def VTKReadSnapshot(self, fieldName, time, numberOfComponents):
        from BasicTools.IO.VtuReader import LoadVtuWithVTK
        from vtk.numpy_interface import dataset_adapter as dsa

        solutionComponentNames = []
        for suffix in primalSolutionComponents[numberOfComponents]:
            solutionComponentNames.append(fieldName+suffix)

        res = []
        for name in solutionComponentNames:
            data = LoadVtuWithVTK(self.solutionFileName)
            npArray = dsa.WrapDataObject(data).GetPointData().GetArray(name)
            res.append(npArray)

        return np.concatenate(res)
    

    def npReadSnapshot(self, fieldName, time, numberOfComponents):
        import pickle

        solutionComponentNames = []
        for suffix in primalSolutionComponents[numberOfComponents]:
            solutionComponentNames.append(fieldName+suffix)

        res = []
        for name in solutionComponentNames:
            pkl_file = open(self.solutionFileName, 'rb')
            npArrayDict = pickle.load(pkl_file)
            pkl_file.close()
            npArray = npArrayDict.get(name)
            res.append(npArray)

        return np.concatenate(res)
