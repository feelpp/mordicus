# -*- coding: utf-8 -*-

import numpy as np
import collections
from Mordicus.Modules.Safran.Containers.Loadings import PressureBC as PBC


def test():

    coefficients = collections.OrderedDict()
    fieldsMap = collections.OrderedDict()
    fields = {}

    coefficients[0.0] = 1.0
    coefficients[1.0] = 1.5
    coefficients[2.0] = 0.2

    fieldsMap[0.0] = "pressure1"
    fieldsMap[1.0] = "pressure2"
    fieldsMap[2.0] = "pressure1"

    fields["pressure1"] = np.zeros(10)
    fields["pressure2"] = np.ones(10)

    loading = PBC.PressureBC("U", "set1")
    loading.SetCoefficients(coefficients)
    loading.SetFieldsMap(fieldsMap)
    loading.SetFields(fields)
    
    loading.__getstate__()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
