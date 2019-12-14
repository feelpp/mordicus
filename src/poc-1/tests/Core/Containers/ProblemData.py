## -*- coding: utf-8 -*-

import numpy as np

from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers.Loadings import LoadingBase as LB


def test():

    solution = Solution.Solution("U", 2, 10, True)
    loading = LB.LoadingBase("set1", "type1")
    #remark: LoadingBase should not be used in use cases
    parameter = np.zeros(2)
    problemData = PD.ProblemData("toto")
    problemData.AddSolution(solution)
    problemData.AddLoading(loading)
    problemData.GetLoadings()
    problemData.GetSolution("U")
    problemData.AddParameter(parameter, 0.0)
    problemData.GetParameterAtTime(0.0)
    problemData.GetParameters()
    problemData.GetParameterDimension()
    problemData.GetParametersTimeSequence()
    problemData.GetParametersList()
    print(problemData)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
