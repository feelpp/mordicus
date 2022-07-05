from logging import getLogger
import py
import sys
import pytest

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
    def __init__(self):
        try:
            sys.argv = ['test_feelpp']
            self.feelpp_env = feelpp.Environment(
                sys.argv, config=feelpp.globalRepository("pyfeelpp-mordicus-tests"))
        except Exception:
            return
            
            


@pytest.fixture(scope="session")
def feelpp_environment():
    return None if not has_feelpp else InitFeelpp().feelpp_env
