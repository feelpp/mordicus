# -*- coding: utf-8 -*-

import os
from Mordicus.Core.IO import StateIO as SIO

def test():

    SIO.SaveState("temp", 1.)
    assert SIO.LoadState("temp") == 1
    os.system("rm -rf temp.pkl")


    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
