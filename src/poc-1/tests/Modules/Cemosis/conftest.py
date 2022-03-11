import sys
import pytest
import feelpp

class InitFeelpp:
    def __init__(self,config):
        try:
            sys.argv=['test_feelpp']
            self.e = feelpp.Environment(sys.argv,config=config)
        except Exception:
            return 

@pytest.fixture(scope="session")
def init_feelpp():
    return InitFeelpp(feelpp.globalRepository("pyfeelpp-tests"))

@pytest.fixture(scope="session")
def init_feelpp_config_local():
    return InitFeelpp(feelpp.localRepository("feelppdb"))
