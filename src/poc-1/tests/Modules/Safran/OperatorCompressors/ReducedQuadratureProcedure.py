# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Modules.Safran.OperatorCompressors import ReducedQuadratureProcedure as RQP




def test():

    integrationWeights = np.arange(20)
    integrands = np.random.rand(10,20)
    reducedIntegrationPointsInitSet = []
    imposedIndices = [1,2]
    
    tolerance = 1.e-6

    s, x = RQP.ComputeReducedIntegrationScheme(integrationWeights, integrands,\
        tolerance, imposedIndices, reducedIntegrationPointsInitSet)


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
    
    
