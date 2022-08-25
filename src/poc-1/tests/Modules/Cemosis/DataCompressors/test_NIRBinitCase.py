import os
# import os.path as osp

import pytest
import sys

from Mordicus.Modules.Cemosis.DataCompressors.NIRBinitCase import * 
import feelpp


@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_NIRB_init_case():
    """ 
    --------------------------------------
            initialize toolbox 
    --------------------------------------
    """
    ## Current Directories
    currentFolder=os.getcwd()

    # model directories 
    toolboxesOptions='heat'
    modelsFolder = f"{currentFolder}/models/" 
    modelsFolder = f"{modelsFolder}{toolboxesOptions}" 
    cfg_path = f"{modelsFolder}/square/square.cfg" 
    geo_path = f"{modelsFolder}/square/square.geo"
    model_path = f"{modelsFolder}/square/square.json"

    # fineness of two grids
    H = 0.1  # CoarseMeshSize 
    h = H**2 # fine mesh size 


    # set the feelpp environment
    config = feelpp.globalRepository(f"nirb/{toolboxesOptions}")
    e=feelpp.Environment(sys.argv, opts = toolboxes_options(toolboxesOptions), config=config)
    e.setConfigFile(cfg_path)

    order =1
    # load model 
    model = loadModel(model_path)

    tbCoarse = setToolbox(H, geo_path, model, order)
    tbFine = setToolbox(h, geo_path, model,order)

    Dmu = loadParameterSpace(model_path)

    currentFolder=os.getcwd()
    modelsFolder= f"{currentFolder}/models/"
    numberOfSnapshot = 3
    fineSnapList, _ = initproblem(numberOfSnapshot, tbFine, tbCoarse, Dmu) 
    assert len(fineSnapList) == numberOfSnapshot 
