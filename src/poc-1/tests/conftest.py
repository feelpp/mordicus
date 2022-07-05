from logging import getLogger
import sys

import py
import pytest
try:
    import feelpp
    import spdlog 
except:
    pass

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
            self.env = feelpp.Environment(
                sys.argv, config=feelpp.globalRepository("pyfeelpp-mordicus-tests"))
            self.logger=spdlog.ConsoleLogger("test_feelpp.log")
        except Exception:
            return


@pytest.fixture(scope="session")
def feelpp_environment():
    print("Setup Feel++")
    yield None if not has_feelpp else InitFeelpp()
    print("\nTeardown Feel++")
    try:
        print("")
    except:
        pass
