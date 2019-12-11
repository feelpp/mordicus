## -*- coding: utf-8 -*-

import numpy as np

from MordicusCore.Containers import Solution
from MordicusCore.Containers import ProblemData as PD
from MordicusCore.Containers.Loadings import LoadingBase


def test():

    solution = Solution.Solution("U", 2, 10, True)
    loading = LoadingBase.LoadingBase()
    parameter = np.zeros(2)
    problemData = PD.ProblemData()
    problemData.AddSolution(solution)
    problemData.SetLoadings([loading])
    problemData.GetSolution("U")
    problemData.AddParameter(parameter, 0.0)
    problemData.GetParameterAtTime(0.0)
    problemData.GetParameters()
    problemData.GetParameterDimension()
    print(problemData)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
