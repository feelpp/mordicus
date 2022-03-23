from Mordicus.Modules.Cemosis.IO import FeelppMeshReader as FMR
import feelpp

def test(init_feelpp):
    r = FMR.FeelppMeshReader(feelpp.create_rectangle()[0])
    m = r.ReadMesh()
    assert m.GetDimensionality() == 2
    print("ok")

if __name__ == "__main__":
    print(test()) # pragma: no cover
