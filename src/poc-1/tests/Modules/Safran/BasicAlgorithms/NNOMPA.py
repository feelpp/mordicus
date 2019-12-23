# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA


def test():

    diag = np.arange(20)
    Phi = np.random.rand(10,20)
    tolerance = 1.e-6

    s, x = NNOMPA.ComputeReducedIntegrationScheme(diag, Phi, tolerance)
    s, x = NNOMPA.ComputeReducedIntegrationScheme(diag, Phi, tolerance, imposedIndices = [0,1], reducedIntegrationPointsInitSet = [0,2])

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
    
    
