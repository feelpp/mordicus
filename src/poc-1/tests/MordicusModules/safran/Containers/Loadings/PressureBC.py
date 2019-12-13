# -*- coding: utf-8 -*-

import numpy as np
import collections
from MordicusModules.safran.Containers.Loadings import PressureBC as PBC


def test():

    coefficients = collections.OrderedDict()
    fieldsMap    = collections.OrderedDict()
    fields       = {}

    coefficients[0.] = 1.
    coefficients[1.] = 1.5
    coefficients[2.] = 0.2

    fieldsMap[0.] = "pressure1"
    fieldsMap[1.] = "pressure2"
    fieldsMap[2.] = "pressure1"
    
    fields["pressure1"] = np.zeros(10)
    fields["pressure2"] = np.ones(10)  

    loading = PBC.PressureBC()
    loading.SetCoefficients(coefficients)
    loading.SetFieldsMap(fieldsMap)
    loading.SetFields(fields)
    
    loading.ComputePressureFieldAtTime(0.5)
    
    print(loading)
    return "ok"


if __name__ == '__main__':
    print(test()) #pragma: no cover
