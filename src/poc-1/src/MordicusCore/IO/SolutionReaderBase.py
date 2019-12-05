# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.Containers.BaseObject import BaseObject


class SolutionReaderBase(BaseObject):
    """
    Class containing the SolutionReaderBase associated to a HF solution file
    """
    
    def __init__(self):
        super(SolutionReaderBase,self).__init__()



    def ReadSnapshot(self, fieldName, time, primality):
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
        raise("Not implemented in ReaderBase")  #pragma: no cover 


        
    def ReadTimeSequenceFromSolutionFile(self):
        """
        Reads the time sequence from the solution file of the HF computation (may be different from the ones defined in the input data file if the solver chose to solve at additional time steps)
        
        Returns
        -------
        np.ndarray
            of size (numberOfSnapshots,)
        """
        raise("Not implemented in ReaderBase")  #pragma: no cover  



    def __str__(self):
        res = "I am a SolutionReaderBase, try instanciating a particular reader instead"
        return res
