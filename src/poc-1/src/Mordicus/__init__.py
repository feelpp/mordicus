# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


__name__ = "Mordicus"
__copyright_holder__ = "Mordicus Consortium"
__copyright_years__ = "2018-2022"
__copyright__ = f"{__copyright_years__}, {__copyright_holder__}"
__license__ = "proprietary - TBD"
__version__ = "0.1"
__description__ = "Mordicus code developped by the FUI MOR_DICUS consortium"
__long_description__ ="The principal objective of the MOR_DICUS project is the develop generic model order reduction software modules for efficient computation (accelerated, real-time), design and fast and reliable analysis for industrial systems, taking into account complex modeling parameters."
__url__ = "https://gitlab.pam-retd.fr/mordicus/mordicus"
__contact__ = ""





def GetTestPath():
    """
    Help function to access the tests path of the library
    """
    import os
    from pathlib import Path

    return os.path.normpath(str(Path(os.path.realpath(__file__)).parents[2]) + os.sep + "tests") + os.sep



def GetTestDataPath():
    """
    Help function to access the TestsData path of the library
    """

    import os

    return os.path.normpath(GetTestPath() + "TestsData") + os.sep



def RunTestFile(srcFilePath):
    """
    Help function to run the tests corresponding to a source file
    """

    import os

    testFolder = GetTestPath()


    relPath = os.path.relpath(os.path.realpath(srcFilePath), testFolder)
    testFile = os.path.join(testFolder, os.path.relpath(relPath, os.path.join("..", "src", "Mordicus")))
    folderFile = os.path.dirname(testFile)

    os.chdir(folderFile)

    os.system( "python "+testFile)


