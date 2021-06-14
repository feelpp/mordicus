import pytest
from Mordicus.Modules.Cemosis.IO import FeelppMeshReader as GMR
from Mordicus import GetTestDataPath

def test_FeelppMeshReader():

    folder = GetTestDataPath() + "feelpp/geo/"

    meshFileName = folder + "cube.geo"

    reader = GMR.FeelppMeshReader(meshFileName,dim=3,realdim=3)
    reader.ReadMesh()

    GMR.ReadMesh(meshFileName)

    
