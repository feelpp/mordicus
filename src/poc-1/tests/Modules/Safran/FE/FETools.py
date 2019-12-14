# -*- coding: utf-8 -*-
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Core import GetTestDataPath


def test():
    
    folder = GetTestDataPath() + "Zset/"

    meshFileName = folder + "cube.geof"

    reader = ZMR.ZsetMeshReader(meshFileName)

    mesh = reader.ReadMesh()
    mesh = ZMR.ReadMesh(meshFileName)
    
    FT.ComputeL2ScalarProducMatrix(mesh, 1)
    FT.ComputeH10ScalarProductMatrix(mesh, 1)
    FT.ComputeFEInterpMatAtGaussPoint(mesh)
    FT.ComputeMecaIntegrator(mesh)
    FT.ComputeNumberOfIntegrationPoints(mesh)
    
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
