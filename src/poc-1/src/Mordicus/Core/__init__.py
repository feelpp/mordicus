# -*- coding: utf-8 -*-

def GetTestDataPath():
    """ 
    Help function to access the TestsData path of the library
    """
    import os
    from pathlib import Path

    return (
        str(Path(__file__).parents[3])
        + os.sep
        + "tests"
        + os.sep
        + "TestsData"
        + os.sep
    )


def GetTestPath():
    """ 
    Help function to access the tests path of the library
    """
    import os
    from pathlib import Path

    return str(Path(__file__).parents[3]) + os.sep + "tests" + os.sep
