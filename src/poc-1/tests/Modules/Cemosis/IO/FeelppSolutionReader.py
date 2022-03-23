from Mordicus.Modules.Cemosis.IO import FeelppSolutionReader as FSR
from Mordicus.Modules.Cemosis.IO import FeelppMeshReader as FMR
from Mordicus import GetTestDataPath
import feelpp

def test(init_feelpp):
    mr = FMR.FeelppMeshReader(feelpp.create_rectangle()[0])
    m = mr.ReadMesh()
    folder = GetTestDataPath() + "Feelpp/"
    solution_name = "field"

    sr = FSR.FeelppSolutionReader(m)
    s = sr.ReadSnapshotComponent(folder+solution_name+".h5")
    assert s.shape[0] == 71
    print("ok")

if __name__ == "__main__":
    print(test()) # pragma: no cover
