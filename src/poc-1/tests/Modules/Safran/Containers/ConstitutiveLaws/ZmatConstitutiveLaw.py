# -*- coding: utf-8 -*-

from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ZmatConstitutiveLaw as ZCL


def test():

    constitutiveLaw = ZCL.ZmatConstitutiveLaw("set1")
    constitutiveLaw.GetSet()
    constitutiveLaw.GetType()
    constitutiveLaw.GetIdentifier()
    constitutiveLaw.GetConstitutiveLawVariables()
    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
