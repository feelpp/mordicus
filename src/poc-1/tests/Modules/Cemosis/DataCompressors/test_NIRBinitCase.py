import os
# import os.path as osp

import pytest
import sys

from Mordicus.Modules.Cemosis.DataCompressors import initCaseNIRB as IC
import feelpp


@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_NIRB_init_case():
    currentFolder=os.getcwd()
    modelsFolder= f"{currentFolder}/models/"
    numberOfSnapshot = 3
    fineSnapList, _, _, _ = IC.initproblem(numberOfSnapshot, modelsFolder=modelsFolder)
    assert len(fineSnapList) == numberOfSnapshot 
