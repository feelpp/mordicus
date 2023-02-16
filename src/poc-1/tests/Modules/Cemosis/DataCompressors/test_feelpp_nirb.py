import os, sys 
import pytest
import feelpp
from Mordicus import GetTestDataPath
from Mordicus.Modules.Cemosis.DataCompressors import nirb 


# desc : (('model_directory', cfg, json, doRectification, doGreedy), 'name-of-the-test')
cases = [
        #  (('testCase/nirb/lid-driven-cavity/', 'cfd2d.cfg', 'cfd2d.json', False), 'lid-driven-cavity w/o rect.'),
        #  (('testCase/nirb/lid-driven-cavity/', 'cfd2d.cfg', 'cfd2d.json', True) , 'lid-driven-cavity rect'),
         (('testCase/nirb/square', 'square.cfg', 'square.json', False, False), 'square2d w/o rect wogreedy'),
         (('testCase/nirb/square', 'square.cfg', 'square.json', True, False) , 'square2d rect wogreedy'),
         (('testCase/nirb/square', 'square.cfg', 'square.json', True, True) , 'square2d rect egreedy'),
         (('testCase/nirb/thermal-fin-3d', 'thermal-fin.cfg', 'thermal-fin.json', False, False), 'thermal-fin-3d w/o rect wogreedy'),
        #  (('testCase/nirb/thermal-fin-3d', 'thermal-fin.cfg', 'thermal-fin.json', True, False) , 'thermal-fin-3d rect wogreedy'),
        ]
# NB: for the name of the test, wogreedy is a keyword standing for "without greedy", and egreedy for "enable greedy" 
cases_params, cases_ids = list(zip(*cases))
nbSnap = 10

def run_offline(model_path, rect, greedy):
    # nbSnap = 10
    nirb_config = feelpp.readJson(model_path)['nirb']
    nirb_config['doRectification'] = rect
    nirb_config['greedy-generation'] = greedy
    nirb_off = nirb.nirbOfflineFeelpp(**nirb_config, nbSnap=nbSnap, initCoarse=greedy)

    nirb_off.getReducedBasis()

    nirb_off.saveData()

    assert nirb_off.checkOrthogonality(), "L2 orthonormalization failed"


def run_online(model_path, rect):
    # nbSnap=6
    nirb_config = feelpp.readJson(model_path)['nirb']
    nirb_config['doRectification'] = rect
    nirb_on = nirb.nirbOnlineFeelpp(**nirb_config)
    err = nirb_on.loadData(nbSnap=nbSnap)
    assert err == 0, "loadData failed"

    mu = nirb_on.nirbOnline.Dmu.element()

    uHh = nirb_on.getOnlineSol(mu)
    uH = nirb_on.getInterpSol(mu)
    uh = nirb_on.getToolboxSol(mu, nirb_on.tbFine)

# @pytest.mark.skip('wait merge branch nirb into develop in feelpp')
@pytest.mark.parametrize("dir,cfg,json,rect,greedy", cases_params, ids=cases_ids)
@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_feelpp_nirb(init_feelpp, dir, cfg, json, rect, greedy):
    e = init_feelpp
    casefile = os.path.join(os.path.dirname(__file__), dir, cfg)
    model_path = os.path.join(os.path.dirname(__file__), dir, json)
    feelpp.Environment.setConfigFile(casefile)

    run_offline(model_path, rect, greedy)
    run_online(model_path, rect)
