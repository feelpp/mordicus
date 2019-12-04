# -*- coding: utf-8 -*-

class LoadingBase(object):
    """
    Class containing a LoadingBase

    Attributes
    ----------
    set : str
        the elements tag on which the loading is applied
    """
        
    def __init__(self):
        self.set  = ""
    

    def SetSet(self, set):
        """
        Parameters
        ----------
        set : str
            the elements tag on which the loading is applied
        """
        assert isinstance(set, str)
        
        self.set = set
        


    def GetSet(self):
        """
        Returns
        -------
        str
            the elements tag on which the loading is applied
        """
        return self.set
        

    def __str__(self):
        from MordicusCore.Containers import Loadings
        allLoadings = [l for l in Loadings.__all__ if "Base" not in str(l)]
        res = "I am a LoadingBase, try instanciating a physical loading among "+str(allLoadings)+" instead"
        return res
