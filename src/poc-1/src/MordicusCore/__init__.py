# -*- coding: utf-8 -*-
__all__ = [
    "Containers",
    "IO",
    "DataCompressors",
    "BasicAlgorithms",
    "OperatorCompressors",
]


def GetTestDataPath():
    """ 
    Help function to access the testsData path of the library
    """
    import os
    from pathlib import Path

    return (
        str(Path(__file__).parents[2])
        + os.sep
        + "tests"
        + os.sep
        + "testsData"
        + os.sep
    )


def GetTestPath():
    """ 
    Help function to access the tests path of the library
    """
    import os
    from pathlib import Path

    return str(Path(__file__).parents[2]) + os.sep + "tests" + os.sep
