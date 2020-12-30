# -*- coding: utf-8 -*-

import numpy as np
import collections
from Mordicus.Modules.Safran.Containers.Loadings import Temperature as T


def test():

    fieldsMap = collections.OrderedDict()
    fields = {}

    fieldsMap[0.0] = "temperature1"
    fieldsMap[1.0] = "temperature2"
    fieldsMap[2.0] = "temperature1"

    fields["temperature1"] = np.zeros(10)
    fields["temperature2"] = np.ones(10)

    loading = T.Temperature("U", "set1")
    loading.SetFieldsMap(fieldsMap)
    loading.SetFields(fields)

    loading.__getstate__()

    print(loading)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
