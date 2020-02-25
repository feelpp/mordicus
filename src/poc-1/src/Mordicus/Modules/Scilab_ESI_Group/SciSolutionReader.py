# -*- coding: utf-8 -*-
import numpy as np

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
import os

def ReadSnapshotComponent(solutionFileName, fieldName, time, primality):
    """
    Reads a snapshots from the solutions of name "fieldName", at time "time" and of primality "primality", from the HF computation

    Parameters
    ----------
    fieldName : str
        name of the solution from which the snapshot is read
    time : float
        time at which the snapshot is read
    primality : bool
        primality of the solution from which the snapshot is read
                
    Returns
    -------
    np.ndarray
        of size (numberOfDofs,)
    """
    reader = SciSolutionReader(solutionFileName=solutionFileName)
    return reader.ReadSnapshotComponent(fieldName, time, primality)

def ReadTimeSequenceFromSolutionFile(solutionFileName):
    """
    Reads the time sequence from the solution file of the HF computation (may be different from the ones defined in the input data file if the solver chose to solve at additional time steps)
    
    Returns
    -------
    np.ndarray
        of size (numberOfSnapshots,)
    """
    reader = SciSolutionReader(solutionFileName=solutionFileName)
    return reader.ReadTimeSequenceFromSolutionFile()

class SciSolutionReader(SolutionReaderBase):
    """
    Class containing a reader for SCILAB use case solution file

    Attributes
    ----------
    solutionFileName : str
    """
    def __init__(self, solutionFileName):
        """
        Parameters
        ----------
        solutionFileName : str, optional
        """
        super(SciSolutionReader, self).__init__()
        assert isinstance(solutionFileName, str)

        folder = str(Path(solutionFileName).parents[0])
        suffix = str(Path(solutionFileName).suffix)
        stem = str(Path(solutionFileName).stem)

        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
            self.solutionFileName = folder + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        else:
            self.solutionFileName = solutionFileName

    def ReadSnapshotComponent(self, fieldName, time, primality):
        # FIXME: indexing variable is not time, just the number of the realization
        # Read CSV file so far
        import csv
        tmp = []
        with open(self.solutionFileName) as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            for row in reader:
                tmp.append(row)
        tmp = np.array(tmp)
        
        i = int(time)
        snapshot = tmp[:,i]
        return snapshot

    def ReadTimeSequenceFromSolutionFile(self):
        # here too
        #return [float(i) for i in range(self.outputSample.getSize())]
        return 1