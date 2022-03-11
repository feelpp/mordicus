from Mordicus.Modules.Cemosis.Containers.Meshes import FeelppMesh as FM
import feelpp
import sys

def test(init_feelpp):

    # e = feelpp.Environment(sys.argv)
    m = feelpp.load(feelpp.mesh(dim=2),"",5)
    mesh = FM.FeelppMesh(m)

    assert mesh.GetDimensionality() == 2
    assert mesh.GetNumberOfNodes() == 5

    return "ok"

if __name__ == "__main__":
    print(test()) # pragme: no cover
