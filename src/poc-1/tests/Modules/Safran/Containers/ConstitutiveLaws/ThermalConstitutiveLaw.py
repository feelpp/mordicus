# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ThermalConstitutiveLaw as TCL
import numpy as np


def test():

    constitutiveLaw = TCL.ThermalConstitutiveLaw("set1")
    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()

    timeIndices = np.array([0.,  100.,  200.,  300.,  400.,  500.,  600.,  700.,  800.,  900., 1000., 2000.])
    coefficients = np.array([2000000., 2200000., 2400000., 2000000., 2400000., 3000000., 2500000., 2400000., 2100000., 2800000., 4000000., 3000000.])
    constitutiveLaw.SetThermalCapacity(timeIndices,coefficients)
    constitutiveLaw.SetThermalConductivity(timeIndices,coefficients)


    vals = [0., 100., 200., 300., 400., 500., 600., 700., 800., 900., 1000., 709.8578384341358, 572.7210459326047, 427.80856157795006, 260.2786026153827, 13.98912997573564, 425.920630842608, 401., 408., 450.]

    resA1 = []
    resA2 = []
    resA3 = []
    for val in vals:
        resA1.append(constitutiveLaw.ComputeCapacity(4.))
        resA2.append(constitutiveLaw.ComputeConductivity(4.))
        resA3.append(constitutiveLaw.ComputeInternalEnergy(22.))

    constitutiveLaw.ComputeCapacity(vals)
    constitutiveLaw.ComputeConductivity(vals)
    constitutiveLaw.ComputeInternalEnergyVectorized(vals)


    print(constitutiveLaw)

    return "ok"





if __name__ == "__main__":
    print(test())  # pragma: no cover


