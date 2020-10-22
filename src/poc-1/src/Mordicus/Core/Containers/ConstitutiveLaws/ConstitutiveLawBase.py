# -*- coding: utf-8 -*-


class ConstitutiveLawBase(object):
    """
    Class containing a ConstitutiveLawBase

    Attributes
    ----------
    set : str
        the elements tag on which the constitutive law is applied
    type : str
        the type of constitutive law (e.g elastic, etc...)
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
            the elements tag on which the constitutive law is applied
        """
        return self.set


    def GetType(self):
        """
        Returns
        -------
        str
            the type of constitutive law
        """
        return self.type


    def GetIdentifier(self):
        """
        Returns
        -------
        couple of string set
            the identifier of constitutive law
        """
        return self.set


    def __str__(self):
        res = "I am a ConstitutiveLawBase, try instanciating a particular physical constitutive law instead"
        return res




if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

