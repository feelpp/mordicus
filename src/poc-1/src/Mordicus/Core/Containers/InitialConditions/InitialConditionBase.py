# -*- coding: utf-8 -*-


class InitialConditionBase(object):
    """
    Class containing a InitialConditionBase
    """

    def __init__(self):
        return


    def ReduceInitialSnapshot(self, reducedOrderBasis, snapshotCorrelationOperator):
        """
        Compresses the initial condition on the reducedOrderBasis, and sets it as parameter of the InitialCondition object
        """
        raise NotImplementedError("Not implemented in InitialConditionBase")  # pragma: no cover


    def GetReducedInitialSnapshot(self):
        """
        Returns
        -------
        np.ndarray
            of size (numberOfModes,)
        """
        raise NotImplementedError("Not implemented in InitialConditionBase")  # pragma: no cover



    def __str__(self):
        res = "I am a InitialConditionBase, try instanciating a particular physical loading instead"
        return res
