# -*- coding: utf-8 -*-
import numpy as np

from MordicusCore.IO.InputReaderBase import InputReaderBase
from BasicTools.IO import ZebulonIO as ZIO

    


def ReadInputTimeSequence(inputFileName):
    """
    Functional API
    
    Reads the time sequence from the Z-set input file "inputFileName" (.inp) (may be different from the ones defined in the solution file if the solver chose to solve at additional time steps)
            
    Parameters
    ----------
    inputFileName : str
        Z-set input file 
                
    Returns
    -------
    np.ndarray
        of size (numberOfSnapshots,)
    """
    reader = ZsetInputReader(inputFileName = inputFileName)
    return reader.ReadInputTimeSequence()


def ConstructLoadingsList(inputFileName):
    """
    Constructs the loadings defined in the Z-set input file "inputFileName" (.inp)
            
    Parameters
    ----------
    inputFileName : str
        Z-set input file 
    
    Returns
    -------
    list
        list of loadings, each one having one of the formats defined in Containers.Loadings
    """    
    reader = ZsetInputReader(inputFileName = inputFileName)
    return reader.ConstructLoadingsList()



class ZsetInputReader(InputReaderBase):
    """
    Class containing a reader for Z-set input file

    Attributes
    ----------
    inputFileName : str
        name of the Z-set input file (.inp)
    inputFile : list
        list containing the input file as parsed by BasicTools.IO.ZebulonIO
    knownLoadingTags : list
        list of loadings tags in the Z-set input file that have been implemented in the current version of the library
    """
    
    def __init__(self, inputFileName = None):
        """
        Parameters
        ----------
        inputFileName : str, optional
        """
        super(ZsetInputReader,self).__init__()
        
        assert isinstance(inputFileName,str) or inputFileName is None
        
        self.inputFileName    = inputFileName     
        self.inputFile        = None

        self.knownLoadingTags  = ["pressure"]
        
        
    def SetInputFile(self):
        """
        Sets the inputFile using the parser in BasicTools.IO.ZebulonIO
        """
        if self.inputFile == None:
            self.inputFile = ZIO.ReadInp2(self.inputFileName)
        else:
            return



    def ReadInputTimeSequence(self):
        self.SetInputFile()
        return ZIO.GetInputTimeSequence(self.inputFile)

                
        
    def ConstructLoadingsList(self):
        import os
        
        self.SetInputFile()
        tables = ZIO.GetTables(self.inputFile)
        bcs = ZIO.GetBoundaryConditions(self.inputFile)

        loadings = []
        for key, value in bcs.items():
            if key in self.knownLoadingTags:
                for bc in bcs[key]:
                    loadings.append(self.ConstructOneLoading(key, bc, tables))
            else:
                print("Boundary Condition '"+key+"' not among knownBCs: "+str([key for key in self.knownLoadingTags]))
                
        return loadings

        

    def ConstructOneLoading(self, key, bc, tables):
        """
        Constructs one loading from the Zset input file

        Parameters
        ----------
        key : str
            Zset keyword for the loading
        bc : list
            list containing the boundary condition data as defined in BasicTools.IO.ZebulonIO
        tables : dict
            list containing the tables data as defined in BasicTools.IO.ZebulonIO
            
        Returns
        -------
        LoadingBase
            the constructed loading in one of the formats defined in Containers.Loadings
        """
        
        import collections
        import os
            
        if key == "pressure":
            from MordicusModules.safran.Containers.Loadings import PressureBC

            loading = PressureBC.PressureBC()
            
            loading.SetSet(bc[0][0])
            
            sequence = tables[bc[0][3]]
            name = os.path.dirname(self.inputFileName)+os.sep+bc[0][2]
            
            coefficients = collections.OrderedDict()
            fieldsMap = collections.OrderedDict()
            for i, time in enumerate(sequence["time"]):
                coefficients[float(time)] = sequence["value"][i]
                fieldsMap[float(time)] = name
                
            loading.SetCoefficients(coefficients)
            loading.SetFieldsMap(fieldsMap)
                
            fields = {name:ZIO.ReadBinaryFile(name)}
                        
            loading.SetFields(fields)
            
            return loading
