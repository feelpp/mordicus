# -*- coding: utf-8 -*-
from MordicusCore.Containers.CompressedFormats.CompressedFormatsBase import CompressedFormatsBase

import numpy as np

class ModesAndCoefficients(CompressedFormatsBase):
    """
    Class containing a ModesAndCoefficients Compressed Format

    Attributes
    ----------
    __storage : dic
        a dictionary containing:
        
        "modes": the reducedOrderBasis, a np.ndarray of size (nbeModes, numberOfDOFs)
        
        "coefficients": the temporal coefficients, a np.ndarray of size (numberOfSnapshots, nbePODModes) 
        
        "times": the time series, a np.ndarray of size (numberOfSnapshots,)
        
        "nbeOfComponents" : number of components of the solution (e.g. 3 for "U" in 3D, or 1 for "T"), an int
        
        "primality" : True for a primal solution and False for a dual solution, a bool       
    """
    def __init__(self, solutionName, times, nbeOfComponents, primality):
        """
        Parameters
        ----------
        solutionName : str
            the name of the compressedFormatsBase object
        times : np.ndarray
        nbeOfComponents : int
        primality : bool
        """
        super(ModesAndCoefficients,self).__init__(solutionName)

        assert (isinstance(times, np.ndarray) and len(times.shape) == 1), str(times)+" must be a 1D numpy.ndarray"

        __storage = {"modes":None,
                     "coefficients":None,
                     "times":times,
                     "nbeOfComponents":nbeOfComponents,
                     "primality":primality}

        self.SetInternalStorage(__storage)
        


    def SetModes(self, modes):
        """
        Sets the modes of the compressed representation, only possible if not already set
        
        Parameters
        ----------
        modes : np.ndarray
        """
        if self.GetInternalStorage()["modes"] is not None:
            raise("Modes already set, cannot set again") #pragma: no cover
        assert (isinstance(modes, np.ndarray) and len(modes.shape) == 2), str(modes)+" must be a 2D numpy.ndarray"
        
        self.GetInternalStorage()["modes"] = modes



    def GetModes(self):
        """
        Returns
        -------
        np.ndarray
            __storage["modes"], of size (nbeModes, numberOfDOFs)
        """
        return self.GetInternalStorage()["modes"]



    def SetCoefficients(self, coefficients):
        """
        Sets the coefficients of the compressed representation, only possible if not already set
        
        Parameters
        ----------
        coefficients : np.ndarray
        """
        if self.GetInternalStorage()["coefficients"] is not None:
            raise("Coefficients already set, cannot set again") #pragma: no cover
        assert (isinstance(coefficients, np.ndarray) and len(coefficients.shape) == 2), str(coefficients)+" must be a 2D numpy.ndarray"
        
        self.GetInternalStorage()["coefficients"] = coefficients
        


    def GetCoefficients(self):
        """
        Returns
        -------
        np.ndarray
            __storage["coefficients"], of size (numberOfSnapshots, nbePODModes)
        """
        return self.GetInternalStorage()["coefficients"]
        


        
    def GetTimes(self):
        """
        Returns
        -------
        np.ndarray
            __storage["times"], of size (numberOfSnapshots,)
        """
        return self.GetInternalStorage()["times"]

        
    def GetNbeOfComponents(self):
        """
        Returns
        -------
        int
            __storage["nbeOfComponents"]
        """
        return self.GetInternalStorage()["nbeOfComponents"]


    def GetPrimality(self):
        """
        Returns
        -------
        bool
            __storage["primality"]
        """
        return self.GetInternalStorage()["primality"]
    

    def GetNumberOfNodes(self):
        """
        Returns
        -------
        int
            number of nodes of the geometrical support of the compressed solution
        """
        numberOfDOFs = self.GetNumberOfDOFs()
        nbeOfComponents = self.GetInternalStorage()["nbeOfComponents"]
        assert(numberOfDOFs%nbeOfComponents == 0), "numberOfDOFs is not a multiple of nbeOfComponents"
        return numberOfDOFs//nbeOfComponents
    

    def GetNumberOfSnapshots(self):
        """
        Returns
        -------
        int
            the number of snapshots
        """
        return self.GetTimes().shape[0]
    
    
    def GetNumberOfModes(self):
        """
        Returns
        -------
        int
            the number of modes
        """
        return self.GetModes().shape[0]
    
    
    
    def GetNumberOfDOFs(self):
        """
        Returns
        -------
        int
            the number of modes
        """
        return self.GetModes().shape[1]
    
        
    def CheckDimensionsConsistence(self):
        """
        Checks to consistency of dimensions between times, coefficients and modes

        """
        (nbeModes1, _) = self.GetModes().shape
        (numberOfSnapshots1,) = self.GetTimes().shape
        (numberOfSnapshots2, nbeModes2) = self.GetCoefficients().shape
        assert (numberOfSnapshots1 == numberOfSnapshots2 and nbeModes1 == nbeModes2), "inconsistence of dimensions"    


    def  __str__(self):
        res = "ModesAndCoefficients"
        return res
