## -*- coding: utf-8 -*-

import numpy as np

from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers.Loadings import LoadingBase as LB
from Mordicus.Core.Containers.InitialConditions import InitialConditionBase as ICB
from Mordicus.Core.Containers.ConstitutiveLaws import ConstitutiveLawBase as CL


def test():

    solution = Solution.Solution("U", 2, 10, True)
    loading = LB.LoadingBase("set1", "type1")
    init = ICB.InitialConditionBase()
    #remark: LoadingBase should not be used in use cases
    constitutiveLaw = CL.ConstitutiveLawBase("set1", "type1")
    parameter = np.zeros(2)
    problemData = PD.ProblemData("toto")
    problemData.SetInitialCondition(init)
    problemData.GetInitialCondition()
    problemData.AddSolution(solution)
    problemData.AddSolution(solution)
    problemData.GetSolution("U")
    problemData.AddLoading(loading)
    problemData.AddLoading(loading)
    problemData.GetLoadings()
    problemData.GetLoadingsOfType("toto")
    problemData.AddConstitutiveLaw(constitutiveLaw)
    problemData.AddConstitutiveLaw(constitutiveLaw)
    problemData.GetConstitutiveLaws()
    problemData.AddParameter(parameter, 0.0)
    problemData.AddParameter(parameter)
    problemData.GetParameterAtTime(0.0)
    problemData.GetParameters()
    problemData.GetParameterDimension()
    problemData.GetParametersTimeSequence()
    problemData.GetParametersList()
    problemData.GetDataFolder()

    import collections
    compressedSnapshots = collections.OrderedDict()
    compressedSnapshots[0.] = np.random.rand(3)
    compressedSnapshots[1.] = np.random.rand(3)
    compressedSnapshots[2.] = np.random.rand(3)
    solution.SetCompressedSnapshots(compressedSnapshots)
    reducedOrderBasis = np.random.rand(3,20)
    problemData.UncompressSolution("U", reducedOrderBasis)

    print(problemData)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
