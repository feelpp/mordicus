# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

from Mordicus.Core.Helpers import FolderHandler as FH
from Mordicus import GetTestDataPath
import os


def test():


    folderHandler = FH.FolderHandler(GetTestDataPath()+'testInit.py')


    folderHandler.SwitchToScriptFolder()
    assert folderHandler.scriptFolder == os.getcwd()

    folderHandler.SwitchToExecutionFolder()
    assert folderHandler.executionFolder == os.getcwd()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
