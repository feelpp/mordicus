# -*- coding: utf-8 -*-


class LoadingBase(object):
    """
    Class containing a LoadingBase

    Attributes
    ----------
    solutionName : str
        the solutionName for which the loading is applied
    set : str
        the elements tag on which the loading is applied
    type : str
        the type of loading (e.g pressure, etc... )
    """

    def __init__(self, solutionName, set, type):
        assert isinstance(set, str)
        assert isinstance(type, str)

        self.solutionName = solutionName
        self.set = set
        self.type = type


    def GetSolutionName(self):
        """
        Returns
        -------
        str
            the solutionName for which the loading is applied
        """
        return self.solutionName
    

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
        couple of strings (set, type)
            the identifier of loading
        """
        return (self.solutionName,self.type,self.set)


    def ComputeContributionToReducedExternalForces(self, time):
        """
        Computes the contribution of the loading to the reduced external forces vector
        """
        raise NotImplementedError("Not implemented in LoadingBase")  # pragma: no cover


    def ReduceLoading(self, mesh, problemData, reducedOrderBasis, operatorCompressionData):
        """
        Carries out the operations needed to reduced the loading, depending on the type of loading (e.g. precomputations)
        """
        raise NotImplementedError("Not implemented in LoadingBase")  # pragma: no cover



    def __str__(self):
        res = "I am a LoadingBase, try instanciating a particular physical loading instead"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


