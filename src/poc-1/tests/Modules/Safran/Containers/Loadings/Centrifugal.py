# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.Loadings import Centrifugal as C
from BasicTools.Containers.UnstructuredMeshCreationTools import CreateCube
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MecaUniformLinearElasticity as MULE
import numpy as np

def test():

    loading = C.Centrifugal("U", "ALLELEMENT")

    assert loading.GetSet() == "ALLELEMENT"
    assert loading.GetType() == "centrifugal"
    assert loading.GetSolutionName() == "U"
    assert loading.GetIdentifier() == ("U","centrifugal","ALLELEMENT")


    loading.SetRotationVelocity({0.:1., 1.:2., 2.:1.5})
    loading.SetCenter([0., 1., 2.])
    loading.SetDirection([0.5, 1., 2.5])
    loading.SetCoefficient(3.14)
    assert loading.GetRotationVelocityAtTime(0.5) == 1.5
    loading.SetCenter([0., 1., 2.])


    mesh = BTUM.BasicToolsUnstructuredMesh(CreateCube(dimensions=[2, 3, 2], spacing=[2.0, 2.0, 2.0], ofTetras=True))
    reducedOrderBases = {"U":np.arange(12*3*5).reshape((5,12*3))}
    problemData = PD.ProblemData("toto")
    constitutiveLaw = MULE.TestMecaConstitutiveLaw("ALLELEMENT", young = 300000., poisson = 0.3, density = 8.6E-09)
    problemData.AddConstitutiveLaw(constitutiveLaw)

    loading.ReduceLoading(mesh, problemData, reducedOrderBases, operatorCompressionData = None)

    """unAssembledReducedUnitCentrifugalVector, integrationWeights =\
        loading.ReduceLoading(mesh, problemData, reducedOrderBases, operatorCompressionData = None)

    np.testing.assert_almost_equal(1e5*np.array([[4.592400e-06, 3.698000e-06, 3.158350e-06, 3.444300e-06,
        4.343000e-06, 4.951450e-06, 3.624900e-06, 2.726200e-06,
        2.147850e-06, 2.399400e-06, 3.302400e-06, 3.949550e-06],
       [1.202280e-05, 9.890000e-06, 8.421550e-06, 9.017100e-06,
        1.115420e-05, 1.269145e-05, 9.197700e-06, 7.060600e-06,
        5.553450e-06, 6.114600e-06, 8.256000e-06, 9.831950e-06],
       [1.945320e-05, 1.608200e-05, 1.368475e-05, 1.458990e-05,
        1.796540e-05, 2.043145e-05, 1.477050e-05, 1.139500e-05,
        8.959050e-06, 9.829800e-06, 1.320960e-05, 1.571435e-05],
       [2.688360e-05, 2.227400e-05, 1.894795e-05, 2.016270e-05,
        2.477660e-05, 2.817145e-05, 2.034330e-05, 1.572940e-05,
        1.236465e-05, 1.354500e-05, 1.816320e-05, 2.159675e-05],
       [3.431400e-05, 2.846600e-05, 2.421115e-05, 2.573550e-05,
        3.158780e-05, 3.591145e-05, 2.591610e-05, 2.006380e-05,
        1.577025e-05, 1.726020e-05, 2.311680e-05, 2.747915e-05]]), 1e5*unAssembledReducedUnitCentrifugalVector)

    np.testing.assert_almost_equal(np.array([1.33333333, 1.33333333, 1.33333333, 1.33333333, 1.33333333,
       1.33333333, 1.33333333, 1.33333333, 1.33333333, 1.33333333, 1.33333333, 1.33333333]), integrationWeights)"""

    np.testing.assert_almost_equal(100.*loading.ComputeContributionToReducedExternalForces(time = 1.5),\
       100.*np.array([0.001704521, 0.004396855, 0.007089188, 0.009781521, 0.012473855]))

    np.testing.assert_almost_equal(1e4*loading.reducedUnitCentrifugalVector,\
       1e4*np.array([5.645040e-05, 1.456152e-04, 2.347800e-04, 3.239448e-04, 4.131096e-04]))

    loading.__getstate__()

    print(loading)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
