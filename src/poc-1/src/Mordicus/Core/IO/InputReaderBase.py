# -*- coding: utf-8 -*-
import numpy as np


class InputReaderBase(object):
    """
    Class containing the InputReaderBase associated to a input data file
    """

    def __init__(self):
        pass

    def ReadInputTimeSequence(self):
        """
        Reads the time sequence from the input data file of the HF computation (may be different from the ones defined in the solution file if the solver chose to solve at additional time steps)
                    
        Returns
        -------
        np.ndarray
            of size (numberOfSnapshots,)
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover

    def ConstructLoadingsList(self):
        """
        Constructs the loadings defined in the input data file of the HF computation
        
        Returns
        -------
        list
            list of loadings, each one having one of the formats defined in Containers.Loadings
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover

    def ConstructConstitutiveLawsVariablesList(self):
        """
        1g one of the formats defined in Containers.Loadings
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover

    def __str__(self):
        res = "I am an InputReaderBase, try instanciating a particular reader instead"
        return res
