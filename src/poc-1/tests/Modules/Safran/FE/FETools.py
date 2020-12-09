# -*- coding: utf-8 -*-
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus import GetTestDataPath
import numpy as np


def test():

    folder = GetTestDataPath() + "Zset/MecaSequential/"

    meshFileName = folder + "cube.geof"

    reader = ZMR.ZsetMeshReader(meshFileName)

    mesh = reader.ReadMesh()
    mesh = ZMR.ReadMesh(meshFileName)

    FT.ComputeL2ScalarProducMatrix(mesh, 1)
    FT.ComputeH10ScalarProductMatrix(mesh, 1)
    FT.ComputeNumberOfIntegrationPoints(mesh)
    FT.ComputeIntegrationPointsTags(mesh, 3)

    length = len(mesh.GetInternalStorage().elements["quad4"].tags["x0"].GetIds())
    FT.IntegrateVectorNormalComponentOnSurface(mesh, "x0", np.ones(length))

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
