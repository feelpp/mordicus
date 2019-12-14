# -*- coding: utf-8 -*-


class LoadingBase(object):
    """
    Class containing a LoadingBase

    Attributes
    ----------
    set : str
        the elements tag on which the loading is applied
    """

    def __init__(self, set, type):
        assert isinstance(set, str)
        assert isinstance(type, str)

        self.set = set
        self.type = type


    def GetSet(self):
        """
        Returns
        -------
        str
            the elements tag on which the loading is applied
        """
        return self.set


    def GetType(self):
        """
        Returns
        -------
        str
            the type of loading
        """
        return self.type
    

    def GetIdentifier(self):
        """
        Returns
        -------
        str
            the identifier of loading
        """
        return self.set+"|"+self.type
    

    def DeleteHeavyData(self):
        """        
        Deletes Heavy Data from loading structure
        """
        raise ("Not implemented in LoadingBase")  # pragma: no cover


    def __str__(self):
        res = "I am a LoadingBase, try instanciating a particular physical loading among instead"
        return res
