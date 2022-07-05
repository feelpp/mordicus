# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.Containers.OperatorCompressionData import OperatorCompressionDataBase as OCDB


def test():

    operatorCompressionDataBase = OCDB.OperatorCompressionDataBase("U")

    assert operatorCompressionDataBase.GetSolutionName() == "U"

    print(operatorCompressionDataBase)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover

