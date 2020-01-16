# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import TestMecaConstitutiveLaw as TMCL
import numpy as np


def test():

    constitutiveLaw = TMCL.TestMecaConstitutiveLaw("set1")
    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()
    constitutiveLaw.GetDensity()
    constitutiveLaw.GetConstitutiveLawVariables()
    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
