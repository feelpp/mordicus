# -*- coding: utf-8 -*-
import numpy as np

from MordicusCore.IO.SolutionReaderBase import SolutionReaderBase


def ReadSnapshot(solutionFileName, fieldName, time, primality=True):
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
    return reader.ReadSnapshot(fieldName, time, primality)


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

    def __init__(self, solutionFileName=None):
        """
        Parameters
        ----------
        solutionFileName : str, optional
        """
        super(ZsetSolutionReader, self).__init__()

        assert isinstance(solutionFileName, str) or solutionFileName is None

        self.solutionFileName = solutionFileName

    def ReadSnapshot(self, fieldName, time, primality=True):
        from BasicTools.IO import UtReader as UR

        if primality == True:
            atIntegrationPoints = False
        else:
            atIntegrationPoints = True  # pragma: no cover
        return UR.ReadFieldFromUt(
            self.solutionFileName,
            fieldName,
            time,
            atIntegrationPoints=atIntegrationPoints,
        )

    def ReadTimeSequenceFromSolutionFile(self):
        from BasicTools.IO import UtReader as UR

        UTMetaData = UR.ReadUTMetaData(self.solutionFileName)
        return UTMetaData["time"][:, 4]
