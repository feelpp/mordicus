from logging import getLogger
import py
import sys
import pytest
import feelpp

class fail_if_not_ok:
    def __init__(self, f):
        self.f = f

    def __call__(self):
        res = self.f()
        assert res.lower() == "ok"

# def pytest_pycollect_makeitem(collector, name, obj):
#     if name == "test" and hasattr(obj, "__call__"):
#         res =  pytest.Function.from_parent(collector, name=name)
#         res.callobj = fail_if_not_ok(obj)
#         return res
#     else:
#         # Fallback to default handler
#         return None


log = getLogger(__name__)
MPI_ARGS = ("mpirun", "-n")
PYTEST_ARGS = (sys.executable, "-mpytest")

@pytest.fixture
def has_mpi4py():
    try:
        import mpi4py
        return True
    except ImportError:
        return False


@pytest.fixture
def has_feelpp():
    try:
        import feelpp
        return True
    except ImportError:
        return False
        
class InitFeelpp:
    def __init__(self,config):
        try:
            sys.argv = ['test_feelpp']
            # self.feelpp_env = feelpp.Environment(
            #     sys.argv, config=config)

            self.env = feelpp.Environment(
                sys.argv, opts= feelpp.backend_options("Iv")
                                .add(feelpp.toolboxes.core.toolboxes_options("heat"))
                                .add(feelpp.toolboxes.core.toolboxes_options("fluid"))
                                .add(feelpp.mor.makeToolboxMorOptions()),
                config=config 
                                )
        except Exception as err:
            print('Exception caught while initializing Feel++: '.format(err))
            return
            
            


# @pytest.fixture(scope="session")
# def feelpp_environment():
#     config = feelpp.globalRepository("pyfeelpp-mordicus-tests")
#     return None if not has_feelpp else InitFeelpp(config=config).feelpp_env


@pytest.fixture(scope="session")
def init_feelpp():
    config = feelpp.globalRepository("pyfeelpp-mordicus-tests")
    # return None if not has_feelpp else InitFeelpp(config=config).env_mor 
    return InitFeelpp(config=config).env 