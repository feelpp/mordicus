# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.Containers.BaseObject import BaseObject



class WriterBase(BaseObject):
    """
    Class containing the WriterBase

    Attributes
    ----------
    outputName : str, optional
        name of the file on disk where the solution is written
    """
    
    def __init__(self, outputName = None):
        """
        Parameters
        ----------
        outputName : str, optional
        """        
        super(WriterBase,self).__init__()
  
        assert outputName == None or isinstance(outputName, str)
        self.outputName = outputName


    def Write(self, mesh, solution):
        """
        Writes a solution on disk satisfying the corresponding format
    
        Parameters
        ----------
        mesh : MeshBase
            the geometric support of the solution from one of the formats defined in Containers.Meshes
        solution : Solution or CompressedFormatsBase
            object to write on disk
        """
        raise("Not implemented in WriterBase")  #pragma: no cover 
        
 
    def __str__(self):       
        from MordicusCore import IO
        allIO = IO.__all__
        allReaders = [a for a in allIO if ("Writer" in a and "Base" not in a)]
        res = "I am a WriterBase, try instanciating a particular reader "+str(allReaders)+" instead"
        return res
