# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure
from Mordicus import GetTestDataPath
import os.path as osp


def test():

    callScript = """
{solverInstall} "{inputRootFolder}/{inputMainFile}"
    """
    # Adding a dataset

    solverCfg = {"solverInstall" : "/bin/bash"}
    solver = ExternalSolvingProcedure(solverCallProcedureType="shell",
                                      solverCfg=solverCfg,
                                      callScript=callScript)
    solver.Execute("ls")
    dataDir = osp.join(GetTestDataPath(), "Core", "IO")

    inputData = {"inputRootFolder"        : dataDir,
                  "inputMainFile"          : "inputMainFile.sh",
                  "inputInstructionFile"   : "inputInstructionFile",
                  "inputMordicusData"      : {"mordicusNpyData": "inputInstructionFile"},
                  "inputResultPath"        : "snapshot.npy",
                  "inputResultType"        : "numpyFile"}
    solver.importMordicusData(inputData)

    print(solver)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
