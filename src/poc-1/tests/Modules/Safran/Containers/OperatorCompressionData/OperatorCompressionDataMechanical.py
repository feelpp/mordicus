# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Modules.Safran.Containers.OperatorCompressionData import OperatorCompressionDataMechanical as OCDM


def test():

    operatorCompressionDataMechanical = OCDM.OperatorCompressionDataMechanical()

    print(operatorCompressionDataMechanical)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover


