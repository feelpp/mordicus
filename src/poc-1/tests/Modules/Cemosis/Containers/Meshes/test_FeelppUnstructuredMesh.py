import pytest
import sys

try:
    from Mordicus.Modules.Cemosis.Containers.Meshes import FeelppUnstructuredMesh as FM
    import feelpp
except:
    pass

@pytest.mark.skipif('feelpp' not in sys.modules,
                    reason="requires the Feel++ library")
def test_feelpp_unstructuredmesh(feelpp_environment):

    m = feelpp.load(feelpp.mesh(dim=2),"",5)
    mesh = FM.FeelppUnstructuredMesh(m)

    assert mesh.GetDimensionality() == 2
    assert mesh.GetNumberOfNodes() == 5

