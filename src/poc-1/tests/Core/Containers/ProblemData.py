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
    assert id(problemData.GetInitialCondition()) == id(init)
    problemData.AddSolution(solution)
    problemData.AddSolution(solution)
    assert id(problemData.GetSolution("U")) == id(solution)
    assert id(problemData.GetSolutions()["U"]) == id(solution)
    problemData.AddLoading(loading)
    problemData.AddLoading(loading)
    problemData.UpdateLoading(loading)
    identifier = loading.GetIdentifier()
    assert id(problemData.GetLoadings()[identifier]) == id(loading)
    assert id(problemData.GetLoadingsOfType("temperature")[0]) == id(loading)
    assert id(problemData.GetLoading("U", "temperature", "set1")) == id(loading)
    problemData.AddConstitutiveLaw(constitutiveLaw)
    problemData.AddConstitutiveLaw(constitutiveLaw)
    identifier = constitutiveLaw.GetIdentifier()
    assert id(problemData.GetConstitutiveLaws()[identifier]) == id(constitutiveLaw)
    problemData.AddParameter(parameter, 0.0)
    problemData.AddParameter(parameter)
    np.testing.assert_almost_equal(problemData.GetParameterAtTime(0.0), np.zeros(2))
    np.testing.assert_almost_equal(problemData.GetParameters()[0.], np.zeros(2))
    assert problemData.GetParameterDimension() == 2
    assert problemData.GetParametersTimeSequence() == [0.]
    np.testing.assert_almost_equal(problemData.GetParametersList()[0], np.zeros(2))
    problemData.SetDataFolder("test")
    assert problemData.GetDataFolder() == "test"
    assert id(problemData.GetLoadingsForSolution("U")[0]) == id(loading)
    assert id(problemData.GetConstitutiveLawsOfType("type1")[0]) == id(constitutiveLaw)
    assert problemData.GetSetsOfConstitutiveOfType("type1") == {'set1'}

    compressedSnapshots = {}
    compressedSnapshots[0.] = np.arange(3) + 0.5
    compressedSnapshots[1.] = np.arange(3) + 1.
    compressedSnapshots[2.] = np.arange(3) + 1.2
    solution.SetCompressedSnapshots(compressedSnapshots)
    reducedOrderBasis = np.arange(60).reshape(3,20)

    problemData.UncompressSolution("U", reducedOrderBasis)
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetSnapshot(0.),
     [130., 134.5, 139., 143.5, 148., 152.5, 157., 161.5, 166., 170.5, 175., 179.5,
      184., 188.5, 193., 197.5, 202., 206.5, 211., 215.5])
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetSnapshot(1.),
     [160., 166., 172., 178., 184., 190., 196., 202., 208., 214., 220., 226., 232., 238.,
      244., 250., 256., 262., 268., 274.])
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetSnapshot(2.),
     [172., 178.6, 185.2, 191.8, 198.4, 205., 211.6, 218.2, 224.8, 231.4, 238., 244.6,
      251.2, 257.8, 264.4, 271., 277.6, 284.2, 290.8, 297.4])

    problemData.CompressSolution("U", reducedOrderBasis, snapshotCorrelationOperator = None)
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetCompressedSnapshot(0.), [ 35815., 104915., 174015.])
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetCompressedSnapshot(1.), [ 45220., 132020., 218820.])
    np.testing.assert_almost_equal(problemData.GetSolution("U").GetCompressedSnapshot(2.), [ 48982., 142862., 236742.])
    problemData.CompressSolution("U", reducedOrderBasis, snapshotCorrelationOperator = np.eye(20))

    problemData.DeleteSolutions()

    print(problemData)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
