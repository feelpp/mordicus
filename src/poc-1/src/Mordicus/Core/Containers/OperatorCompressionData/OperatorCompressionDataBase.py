# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#



class OperatorCompressionDataBase(object):
    """
    Class containing an OperatorCompressionDataBase

    Attributes
    ----------
    solutionName : str
        the solutionName whose computation is reduced
    """

    def __init__(self, solutionName):
        assert isinstance(solutionName, str)

        self.solutionName = solutionName


    def GetSolutionName(self):
        """
        Returns
        -------
        str
            the solutionName whose computation is reduced
        """
        return self.solutionName


    def __str__(self):
        res = "I am an OperatorCompressionDataBase, try instanciating a particular OperatorCompressionData"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

