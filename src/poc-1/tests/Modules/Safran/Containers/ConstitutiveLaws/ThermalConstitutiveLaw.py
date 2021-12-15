# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ThermalConstitutiveLaw as TCL
import numpy as np


def test():

    constitutiveLaw = TCL.ThermalConstitutiveLaw("set1")

    assert constitutiveLaw.GetSet() == 'set1'
    assert constitutiveLaw.GetType() == 'thermal'
    assert constitutiveLaw.GetIdentifier() == ('thermal', 'set1')

    timeIndices = np.array([0.,  100.,  200.,  300.,  400.,  500.,  600.,  700.,  800.,  900., 1000., 2000.])
    coefficients = np.array([2000000., 2200000., 2400000., 2000000., 2400000., 3000000., 2500000., 2400000., 2100000., 2800000., 4000000., 3000000.])
    constitutiveLaw.SetThermalCapacity(timeIndices,coefficients)
    constitutiveLaw.SetThermalConductivity(timeIndices,coefficients)


    vals = [0., 100., 200., 300., 400., 500., 600., 700., 800., 900., 1000., 709.8578384341358, 572.7210459326047, 427.80856157795006, 260.2786026153827, 13.98912997573564, 425.920630842608, 401., 408., 450.]

    assert constitutiveLaw.ComputeCapacity(4.) == 2008000.
    assert constitutiveLaw.ComputeConductivity(4.) == 2008000.
    assert constitutiveLaw.ComputeInternalEnergy(22.) == 44484000.

    ref = np.array([2000000., 2200000., 2400000., 2000000., 2400000., 3000000.,
              2500000., 2400000., 2100000., 2800000., 4000000., 2370426.48469759,
              2636394.77033698, 2566851.3694677,  2158885.58953847, 2027978.25995147,
              2555523.78505565, 2406000., 2448000., 2700000.])
    np.testing.assert_almost_equal(constitutiveLaw.ComputeCapacity(vals), ref)
    np.testing.assert_almost_equal(constitutiveLaw.ComputeConductivity(vals), ref)
    ref = 1.e-9*np.array([0.00000000e+00, 2.10000000e+08, 4.40000000e+08, 6.60000000e+08,\
           8.80000000e+08, 1.15000000e+09, 1.42500000e+09, 1.67000000e+09,\
           1.89500000e+09, 2.14000000e+09, 2.48000000e+09, 1.69351305e+09,\
           1.35494226e+09, 9.49060496e+08, 5.77401626e+08, 2.81739557e+07,\
           9.44225151e+08, 8.82403000e+08, 8.99392000e+08, 1.00750000e+09])
    np.testing.assert_almost_equal(1.e-9*constitutiveLaw.ComputeInternalEnergyVectorized(vals), ref)

    print(constitutiveLaw)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
