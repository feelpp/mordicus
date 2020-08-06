 # -*- coding: utf-8 -*-
from Mordicus.Core.Helpers import FolderHandler as FH


def test():


    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()
    folderHandler.SwitchToExecutionFolder()

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
