# -*- coding: utf-8 -*-
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Core import GetTestDataPath


def test():
    
    folder = GetTestDataPath() + "Zset/MecaSequential/"

    meshFileName = folder + "cube.geof"

    reader = ZMR.ZsetMeshReader(meshFileName)

    mesh = reader.ReadMesh()
    mesh = ZMR.ReadMesh(meshFileName)
    
    FT.ComputeL2ScalarProducMatrix(mesh, 1)
    FT.ComputeH10ScalarProductMatrix(mesh, 1)
    FT.ComputeFEInterpMatAtGaussPoint(mesh)
    FT.ComputeMecaIntegrator(mesh)
    FT.ComputeNumberOfIntegrationPoints(mesh)
    FT.ComputeIntegrationPointsTags(mesh, 3)
    
    import numpy as np
    length = len(mesh.GetInternalStorage().elements["quad4"].tags["x0"].GetIds())
    FT.IntegrateVectorNormalComponentOnSurface(mesh, "x0", np.ones(length))
    
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
