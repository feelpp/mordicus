# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#



class OnlineDataBase(object):
    """
    Class containing an OnlineDataBase
    """

    def __init__(self):
        return


    def __str__(self):
        res = "I am an OnlineDataBase, try instanciating a particular OnlineData"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

