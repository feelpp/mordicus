# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MecaUniformLinearElasticity as MULE


def test():

    young = 300000.
    poisson = 0.3
    density = 8.6E-09

    constitutiveLaw = MULE.TestMecaConstitutiveLaw("set1", young, poisson, density)
    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()
    constitutiveLaw.GetDensity()
    constitutiveLaw.GetConstitutiveLawVariables()
    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
