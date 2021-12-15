# -*- coding: utf-8 -*-
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Core.IO import StateIO as SIO
from Mordicus import GetTestDataPath, GetTestPath
import numpy as np


def test():

    folder = GetTestDataPath() + "Zset/"

    meshFileName = folder + "smallcube.geof"

    reader = ZMR.ZsetMeshReader(meshFileName)

    mesh = reader.ReadMesh()
    mesh = ZMR.ReadMesh(meshFileName)

    res = {}
    res['sparseMatrix'] = {}
    res['array'] = {}
    res['list'] = {}

    res['sparseMatrix']['ComputeL2ScalarProducMatrix'] = FT.ComputeL2ScalarProducMatrix(mesh, 1)
    res['sparseMatrix']['ComputeH10ScalarProductMatrix'] = FT.ComputeH10ScalarProductMatrix(mesh, 1)
    res['array']['ComputeJdetAtIntegPoint'] = np.array(FT.ComputeJdetAtIntegPoint(mesh))

    temp = FT.ComputePhiAtIntegPoint(mesh)
    res['array']['ComputePhiAtIntegPoint'] = temp[0]
    res['sparseMatrix']['ComputePhiAtIntegPoint'] = temp[1]

    temp = FT.ComputeGradPhiAtIntegPoint(mesh)
    res['array']['ComputeGradPhiAtIntegPoint'] = temp[0]
    for i, dat in enumerate(temp[1]):
        res['sparseMatrix']['ComputeGradPhiAtIntegPoint_'+str(i)] = dat

    res['array']['ComputeNormalsAtIntegPoint'] = FT.ComputeNormalsAtIntegPoint(mesh)
    res['array']['ComputeNumberOfIntegrationPoints'] = np.array(FT.ComputeNumberOfIntegrationPoints(mesh))

    listOfTags = FT.ComputeIntegrationPointsTags(mesh, 3)

    res['list']['ComputeIntegrationPointsTags'] = listOfTags

    temp = FT.ComputeIndicesOfIntegPointsPerMaterial(listOfTags, set(["EVP","ELAS"]))

    res['array']['ComputeIndicesOfIntegPointsPerMaterial_1'] = temp["EVP"]
    res['array']['ComputeIndicesOfIntegPointsPerMaterial_2'] = temp["ELAS"]

    length = len(mesh.GetInternalStorage().elements["tri6"].tags["x0"].GetIds())
    fields = {"pressure1":np.ones(length)}

    res['array']['CellDataToIntegrationPointsData'] = FT.CellDataToIntegrationPointsData(mesh, fields, "x0", relativeDimension = -1)[0]
    res['array']['IntegrationPointsToCellData']     = FT.CellDataToIntegrationPointsData(mesh, fields, "x0", relativeDimension = -1)[0]

    #SIO.SaveState(GetTestPath()+"Modules/Safran/FE/ref/ref", res, extension = "res")
    #1./0.

    ref = SIO.LoadState(GetTestPath()+"Modules/Safran/FE/ref/ref", extension = "res")

    for method in ref['sparseMatrix'].keys():
        np.testing.assert_almost_equal(ref['sparseMatrix'][method].todense(), res['sparseMatrix'][method].todense())
    for method in ref['array'].keys():
        np.testing.assert_almost_equal(ref['array'][method], res['array'][method])
    for method in ref['list'].keys():
        assert ref['list'][method] == res['list'][method]

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover