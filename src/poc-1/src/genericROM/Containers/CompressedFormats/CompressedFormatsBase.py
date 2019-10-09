# -*- coding: utf-8 -*-
from genericROM.Containers.BaseObject import BaseObject

class CompressedFormatsBase(BaseObject):
    """
    Class containing a CompressedFormatsBase


    Attributes
    ----------
    __name : str
        the name given to the compressedFormatsBase object
    """
    
    def __init__(self, __name):
        """
        Parameters
        ----------
        __name : str
            the name of the compressedFormatsBase object
        """
        super(CompressedFormatsBase,self).__init__()  
        assert isinstance(__name, str)
        self.__name = __name
    

    def GetName(self):
        """
        Returns
        -------
        str
            the name of the compressedFormatsBase object
        """
        return self.__name
        
        
    def __str__(self):
        from genericROM.Containers import CompressedFormats
        res = "I am a CompressedFormatsBase, try instanciating a compressed format among "+str(CompressedFormats.__all__)+" instead"
        return res

        

def CheckIntegrity():

    compressedFormatsBase = CompressedFormatsBase("toto")
    compressedFormatsBase.GetName()
    print(compressedFormatsBase)
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
