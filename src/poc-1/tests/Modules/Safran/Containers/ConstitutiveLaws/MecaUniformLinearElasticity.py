# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MecaUniformLinearElasticity as MULE
import numpy as np

def test():

    young = 300000.
    poisson = 0.3
    density = 8.6E-09

    constitutiveLaw = MULE.TestMecaConstitutiveLaw('set1', young, poisson, density)

    assert constitutiveLaw.GetSet() == 'set1'
    assert constitutiveLaw.GetType() == 'mechanical'
    assert constitutiveLaw.GetIdentifier() == ('mechanical', 'set1')
    assert constitutiveLaw.GetDensity() == density

    lawVars = constitutiveLaw.GetConstitutiveLawVariables()
    assert lawVars['nstatv'] == 0
    np.testing.assert_almost_equal(lawVars['ddsdde'], np.array([[403846.15384615, 173076.92307692, 173076.92307692,
             0.        ,      0.        ,      0.        ],
       [173076.92307692, 403846.15384615, 173076.92307692,
             0.        ,      0.        ,      0.        ],
       [173076.92307692, 173076.92307692, 403846.15384615,
             0.        ,      0.        ,      0.        ],
       [     0.        ,      0.        ,      0.        ,
        115384.61538462,      0.        ,      0.        ],
       [     0.        ,      0.        ,      0.        ,
             0.        , 115384.61538462,      0.        ],
       [     0.        ,      0.        ,      0.        ,
             0.        ,      0.        , 115384.61538462]]))
    assert lawVars['flux'] == ['sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']
    assert lawVars['grad'] == ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31']
    assert lawVars['var_int'] == []
    assert lawVars['var_aux'] == []
    assert lawVars['var_extra'] == []
    assert lawVars['var'] == ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31',\
            'sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']

    print(constitutiveLaw)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
