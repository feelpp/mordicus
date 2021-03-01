## -*- coding: utf-8 -*-

import numpy as np

from Mordicus.Core.Containers import Solution
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Modules.Safran.Containers.Loadings import Temperature as T
from Mordicus.Core.Containers.InitialConditions import InitialConditionBase as ICB
from Mordicus.Core.Containers.ConstitutiveLaws import ConstitutiveLawBase as CL


def test():

    solution = Solution.Solution("U", 2, 10, True)
    loading = T.Temperature("U", "set1")
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
    problemData.UpdateLoading(loading)
    problemData.GetLoadings()
    problemData.GetLoadingsOfType("type1")
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
    problemData.SetDataFolder("toto")
    problemData.GetDataFolder()
    problemData.GetLoadingsForSolution("U")
    problemData.GetConstitutiveOfType("type1")
    problemData.GetSetsOfConstitutiveOfType("type1")

    import collections
    compressedSnapshots = collections.OrderedDict()
    compressedSnapshots[0.] = np.random.rand(3)
    compressedSnapshots[1.] = np.random.rand(3)
    compressedSnapshots[2.] = np.random.rand(3)
    solution.SetCompressedSnapshots(compressedSnapshots)
    reducedOrderBasis = np.random.rand(3,20)
    problemData.UncompressSolution("U", reducedOrderBasis)
    problemData.DeleteSolutions()

    print(problemData)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
