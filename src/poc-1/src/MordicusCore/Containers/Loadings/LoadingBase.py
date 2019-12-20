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
        self.set = ""

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
        res = "I am a LoadingBase, try instanciating a particular physical loading among instead"
        return res
