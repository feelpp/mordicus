# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
from BasicTools.IO import UtReader as UR


primalSolutionComponents = {1:[""], 2:["1", "2"], 3:["1", "2", "3"]}

dualSolutionComponents = {1:[""], 3:["11", "22", "12"], 6:["11", "22", "33", "12", "23", "31"]}
convertZsetConvention = {"11":(1.,"11"), "22":(1.,"22"), "33":(1.,"33"), "12":(1.,"12"), "23":(1.,"23"), "31":(1.,"31")}

#dualSolutionComponents = {1:[""], 3:["11", "22", "12"], 6:["11", "22", "33", "12", "31", "23"]}
#convertZsetConvention = {"11":(1.,"11"), "22":(1.,"22"), "33":(1.,"33"), "12":(1.,"12"), "23":(1.,"23"), "31":(1.,"31")}

def ReadSnapshotComponent(solutionFileName, fieldName, time, primality=True):
    """
    Functional API

    Reads a snapshots from the Z-set solution file "solutionFileName" (.ut), at time "time" and of primality "primality", from the HF computation

    Parameters
    ----------
    solutionFileName : str
        Z-set solution file
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
    reader = ZsetSolutionReader(solutionFileName=solutionFileName)
    return reader.ReadSnapshotComponent(fieldName, time, primality)


def ReadTimeSequenceFromSolutionFile(solutionFileName):
    """
    Reads the time sequence from the Z-set solution file "solutionFileName" (.ut) (may be different from the ones defined in the input data file if the solver chose to solve at additional time steps)

    Parameters
    ----------
    solutionFileName : str
        Z-set solution file

    Returns
    -------
    np.ndarray
        of size (numberOfSnapshots,)
    """
    reader = ZsetSolutionReader(solutionFileName=solutionFileName)
    return reader.ReadTimeSequenceFromSolutionFile()


class ZsetSolutionReader(SolutionReaderBase):
    """
    Class containing a reader for Z-set solution file

    Attributes
    ----------
    solutionFileName : str
        name of the Z-set solution file (.ut)
    """

    def __init__(self, solutionFileName):
        """
        Parameters
        ----------
        solutionFileName : str, optional
        """
        super(ZsetSolutionReader, self).__init__()

        assert isinstance(solutionFileName, str)

        folder = str(Path(solutionFileName).parents[0])
        suffix = str(Path(solutionFileName).suffix)
        stem = str(Path(solutionFileName).stem)

        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
            solutionFileName = folder + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        else:
            solutionFileName = solutionFileName

        self.reader = UR.UtReader()
        self.reader.SetFileName(solutionFileName)
        self.reader.ReadMetaData()



    def ReadSnapshotComponent(self, fieldName, time, primality=True):

        self.reader.atIntegrationPoints = not primality
        self.reader.SetFieldNameToRead(fieldName)
        self.reader.SetTimeToRead(time=time)

        return self.reader.ReadField()


    def ReadSnapshot(self, fieldName, time, numberOfComponents, primality=True):

        solutionComponentNames = []
        if primality == True:
            for suffix in primalSolutionComponents[numberOfComponents]:
                solutionComponentNames.append(fieldName+suffix)
        else:
            for suffix in dualSolutionComponents[numberOfComponents]:
                solutionComponentNames.append(fieldName+suffix)

        res = []
        for name in solutionComponentNames:
            res.append(self.ReadSnapshotComponent(name, time, primality))

        return np.concatenate(res)


    def ReadSnapshotComponentTimeSequence(self, fieldName, timeSequence, primality=True):

        res = []
        for time in timeSequence:
            res.append(self.ReadSnapshotComponent(fieldName, time, primality))

        return np.array(res)


    """def ReadSnapshotTimeSequenceAndAddToSolution(self, solution, timeSequence, fieldName):

        primality = solution.GetPrimality()
        numberOfComponents = solution.GetNbeOfComponents()

        for t in timeSequence:
            solution.AddSnapshot(self.ReadSnapshot(fieldName, t, numberOfComponents, primality), t)"""


    def ReadTimeSequenceFromSolutionFile(self):

        return self.reader.time[:, 4]


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
