from Mordicus.Modules.Cemosis.Containers.Meshes import FeelppUnstructuredMesh as FM
import feelpp
import sys

def test_feelpp_unstructuredmesh(feelpp_environment):

    m = feelpp.load(feelpp.mesh(dim=2),"",5)
    mesh = FM.FeelppUnstructuredMesh(m)

    assert mesh.GetDimensionality() == 2
    assert mesh.GetNumberOfNodes() == 5

if __name__ == "__main__":
    print(test()) # pragme: no cover
