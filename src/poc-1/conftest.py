import pytest
 
class fail_if_not_ok:
    def __init__(self, f):
        self.f = f

    def __call__(self):
        res = self.f()
        assert res.lower() == "ok"

def pytest_pycollect_makeitem(collector, name, obj):
    if name == "test" and hasattr(obj, "__call__"):
        # Collect CheckIntegrity functions
        # Decorate them to detect failing return values 
        res =  pytest.Function.from_parent(collector, name=name)
        res.callobj = fail_if_not_ok(obj)
        return res 
    else:
        # Fallback to default handler
        return None