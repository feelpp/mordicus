# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ThermalConstitutiveLaw as TCL
import numpy as np


def test():

    constitutiveLaw = TCL.ThermalConstitutiveLaw("set1")
    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()
    constitutiveLaw.SetThermalCapacity([0., 100.],[1., 2.])
    constitutiveLaw.SetThermalConductivity([0., 100.],[1., 2.])
    constitutiveLaw.ComputeConstitutiveLaw(4.)
    print(constitutiveLaw)


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
