# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


import os
from Mordicus.Core.IO import StateIO as SIO

def test():

    SIO.SaveState("temp", 1.)
    assert SIO.LoadState("temp") == 1
    os.system("rm -rf temp.pkl")


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
