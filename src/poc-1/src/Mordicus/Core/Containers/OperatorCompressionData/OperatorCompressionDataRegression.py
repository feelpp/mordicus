# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OperatorCompressionData.OperatorCompressionDataBase import OperatorCompressionDataBase



class OperatorCompressionDataRegression(OperatorCompressionDataBase):
    """
    Class containing an OperatorCompressionDataRegression

    Attributes
    ----------
    model : sklearn.model_selection._search.GridSearchCV
        regressor whose hyperparameters have been optimized by GridSearchCV
    scalerParameters : sklearn.preprocessing._data.StandardScaler
        scaler for the input of the regression (the parameters of the problem)
    scalerCoefficients : sklearn.preprocessing._data.StandardScaler
        scaler for the output of the regression (the coefficients on the
        reduced solution on the reducedOrderBasis - compressedSnapshots)
    """

    def __init__(self, solutionName):
        super(OperatorCompressionDataRegression, self).__init__(solutionName)

        self.model = None
        self.scalerParameters = None
        self.scalerCoefficients = None


    def SetModel(self, model):
        """
        Sets the regressor

        Parameters
        ----------
        model : sklearn.model_selection._search.GridSearchCV
            regressor whose hyperparameters have been optimized by GridSearchCV
        """
        self.model = model


    def SetScalerParameters(self, scalerParameters):
        """
        Sets the scaler for the parameters

        Parameters
        ----------
        scalerParameters : sklearn.preprocessing._data.StandardScaler
            scaler for the input of the regression (the parameters of the problem)
        """
        self.scalerParameters = scalerParameters


    def SetScalerCoefficients(self, scalerCoefficients):
        """
        Sets the scaler for the coefficients

        Parameters
        ----------
        scalerCoefficients : sklearn.preprocessing._data.StandardScaler
            scaler for the output of the regression (the coefficients on the
            reduced solution on the reducedOrderBasis - compressedSnapshots)
        """
        self.scalerCoefficients = scalerCoefficients


    def GetModel(self):
        """
        Returns the regressor

        Returns
        -------
        sklearn.model_selection._search.GridSearchCV
            regressor whose hyperparameters have been optimized by GridSearchCV
        """
        return self.model


    def GetScalerParameters(self):
        """
        Returns the scaler for the parameters

        Returns
        -------
        sklearn.preprocessing._data.StandardScaler
            scaler for the input of the regression (the parameters of the problem)
        """
        return self.scalerParameters


    def GetScalerCoefficients(self):
        """
        Returns the scaler for the coefficients

        Returns
        -------
        sklearn.preprocessing._data.StandardScaler
            scaler for the output of the regression (the coefficients on the
            reduced solution on the reducedOrderBasis - compressedSnapshots)
        """
        return self.scalerCoefficients



    def __str__(self):
        res = "OperatorCompressionDataRegression"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


