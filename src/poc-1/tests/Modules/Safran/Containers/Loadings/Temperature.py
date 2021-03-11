# -*- coding: utf-8 -*-

import numpy as np
#import collections
from Mordicus.Modules.Safran.Containers.Loadings import Temperature as T


def test():

    fields = {}
    
    fieldsMapTimes = [0., 1., 2.]
    fieldsMapValues = ["temperature1", "temperature1", "temperature2"]

    fields["temperature1"] = np.zeros(10)
    fields["temperature2"] = np.ones(10)

    loading = T.Temperature("U", "set1")
    loading.SetFieldsMap(fieldsMapTimes, fieldsMapValues)
    loading.SetFields(fields)
    loading.UpdateLoading(loading)

    loading.__getstate__()

    print(loading)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
