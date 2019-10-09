# -*- coding: utf-8 -*-
import os

class BaseObject(object):
    """
    Class containing a Base Object, with an internal storage hidden to all its children classes

    Attributes
    ----------
    __storage : typeToDefine
    """
    def __init__(self):
        self.__storage = None
    
    
    def SetInternalStorage(self, __storage):
        """
        Sets the internal storage
        
        Parameters
        ----------
        __storage : typeToDefine
        """
        if self.__storage  is not None:
            print("Internal storage already set. Replacing it anyway.")  #pragma: no cover
        self.__storage = __storage
        
        
        
    def GetInternalStorage(self):
        """
        Returns
        -------
        typeToDefine
            internal storage
        """
        if self.__storage is None:
            raise("Please set internal storage")  #pragma: no cover
        return self.__storage
    
    

    def Save(self, fileName):
        """
        Saves object on disk using pickle
        
        Parameters
        ----------
        fileName : str
        """
        import pickle
        
        assert (type(fileName) == str)

        output = open(fileName+'.pkl', 'wb')
        pickle.dump(self, output)
        output.close()
        
        
        
    def __str__(self):
        res = "I am a BaseObject, try instanciating a particular object from the library instead."
        return res


def CheckIntegrity():

    baseObject = BaseObject()
    baseObject.SetInternalStorage("toto")
    baseObject.GetInternalStorage()
    
    baseObject.Save("test")
    os.system("rm -rf test.pkl")
    
    print(baseObject)
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
