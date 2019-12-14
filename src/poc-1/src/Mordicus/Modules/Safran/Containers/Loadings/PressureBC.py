# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.Loadings.LoadingBase import LoadingBase
import numpy as np
import collections


class PressureBC(LoadingBase):
    """
    Class containing a Loading of type pressure boundary condition. A pressure vector over the elements of set at time t is given by : coefficients[ t ] * fields[ fieldsMap[ t ] ]
    

    Attributes
    ----------
    coefficients : collections.OrderedDict()
        dictionary with time indices (float) as keys and temporal coefficients (float) as values
    fieldsMap    : collections.OrderedDict()
        dictionary with time indices (float) as keys and pressure vectors tags (str) as values
    fields       : dict
        dictionary with pressure vectors tags (str) keys and pressure vectors (np.ndarray of size (numberOfElementsInSet,)) as values
    """

    def __init__(self, set):
        assert isinstance(set, str)
        
        super(PressureBC, self).__init__(set, "pressure")

        self.coefficients = collections.OrderedDict
        self.fieldsMap = {}
        self.fields = {}

    def SetCoefficients(self, coefficients):
        """
        Sets the coeffients attribute of the class
        
        Parameters
        ----------
        coefficients : collections.OrderedDict
        """
        # assert type of coefficients
        assert isinstance(coefficients, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(coefficients.keys())]
        )
        assert np.all(
            [
                isinstance(key, (float, np.float64))
                for key in list(coefficients.values())
            ]
        )

        self.coefficients = coefficients

    def SetFieldsMap(self, fieldsMap):
        """
        Sets the fieldsMap attribute of the class
        
        Parameters
        ----------
        fieldsMap : collections.OrderedDict
        """
        # assert type of fieldsMap
        assert isinstance(fieldsMap, collections.OrderedDict)
        assert np.all(
            [isinstance(key, (float, np.float64)) for key in list(fieldsMap.keys())]
        )
        assert np.all([isinstance(key, str) for key in list(fieldsMap.values())])

        self.fieldsMap = fieldsMap

    def SetFields(self, fields):
        """
        Sets the fields attribute of the class
        
        Parameters
        ----------
        fields : dict
        """
        # assert type of fields
        assert isinstance(fields, dict)
        assert np.all([isinstance(key, str) for key in list(fields.keys())])
        assert np.all(
            [isinstance(value, np.ndarray) for value in list(fields.values())]
        )

        self.fields = fields

    def ComputePressureFieldAtTime(self, time):
        """
        Computes the pressure vector at time, using TimeInterpolation
        
        Parameters
        ----------
        time : float
        
        Returns
        -------
        np.ndarray
            pressure vector at time
        """

        # assert type of time
        assert isinstance(time, (float, np.float64))

        from Mordicus.Core.BasicAlgorithms import TimeInterpolation as TI

        # compute coefficient at time
        coefficient = TI.TimeInterpolation(
            time, list(self.coefficients.keys()), list(self.coefficients.values())
        )

        # compute vector field at time
        vectorField = TI.TimeInterpolation(
            time,
            list(self.fieldsMap.keys()),
            self.fields,
            list(self.fieldsMap.values()),
        )

        return coefficient * vectorField
    
    
    def DeleteHeavyData(self):
        """        
        Deletes Heavy Data from PressureBC structure
        """
        for f in self.fields.keys():
            self.fields[f] = None


    def __str__(self):
        res = "Loading \n"
        res += "Set : " + self.GetSet()
        return res
