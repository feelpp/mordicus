# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#


from BasicTools.FE import FETools as FT
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
import numpy as np


def ComputeL2ScalarProducMatrix(mesh, numberOfComponents):
    """
    Computes the L2 scalar product used to compute the correlations
    between the primal solution snapshots. The numberOfComponents
    depends on the solution type: 3 for solid mechanics in 3D, or 1 for
    thermal in any dimension

    Optimal input mesh format is BasicToolsUnstructuredMesh.

    Parameters
    ----------
    mesh : MeshBase
            the geometric support of the solution from one of the formats defined in Containers.Meshes
    numberOfComponents : int
        the number of components of the primal variable snapshots

    Returns
    -------
    scipy.sparse.csr
        the sparse matrix of the L2 scalar product
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeL2ScalarProducMatrix(unstructuredMesh, numberOfComponents)


def ComputeH10ScalarProductMatrix(mesh, numberOfComponents):
    """
    Computes the H10 scalar product matrix.

    Optimal input mesh format is BasicToolsUnstructuredMesh.

    Parameters
    ----------
    numberOfComponents : int
        the number of components of the primal variable snapshots

    Returns
    -------
    scipy.sparse.csr
        the sparse matrix of the H10 scalar product
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeH10ScalarProductMatrix(unstructuredMesh, numberOfComponents)


def ComputeJdetAtIntegPoint(mesh, elementSets = None, relativeDimension = 0):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeJdetAtIntegPoint(unstructuredMesh, elementSets, relativeDimension)


def ComputePhiAtIntegPoint(mesh, elementSets = None, relativeDimension = 0):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputePhiAtIntegPoint(unstructuredMesh, elementSets, relativeDimension)


def ComputeGradPhiAtIntegPoint(mesh, elementSets = None, relativeDimension = 0):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeGradPhiAtIntegPoint(unstructuredMesh, elementSets, relativeDimension)


def ComputeNormalsAtIntegPoint(mesh, elementSets = None):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeNormalsAtIntegPoint(unstructuredMesh, elementSets)


def ComputeNumberOfIntegrationPoints(mesh):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)
    _, _, _, numberOfIntegrationPoints = FT.PrepareFEComputation(unstructuredMesh)

    return numberOfIntegrationPoints


def ComputeIntegrationPointsTags(mesh, dimension = None):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeIntegrationPointsTags(unstructuredMesh, dimension)


def ComputeIndicesOfIntegPointsPerMaterial(listOfTags, keysConstitutiveLaws):

    materialKeyPerIntegrationPoint = ComputeMaterialKeyPerIntegrationPoint(listOfTags, keysConstitutiveLaws)

    numberOfIntegrationPoints = len(listOfTags)

    IndicesOfIntegPointsPerMaterial = {}
    arange = np.arange(numberOfIntegrationPoints)
    for key in keysConstitutiveLaws:
        IndicesOfIntegPointsPerMaterial[key] = arange[np.array(materialKeyPerIntegrationPoint) == key]

    return IndicesOfIntegPointsPerMaterial


def ComputeMaterialKeyPerIntegrationPoint(listOfTags, keysConstitutiveLaws):

    numberOfIntegrationPoints = len(listOfTags)

    materialKeyPerIntegrationPoint = []
    for i in range(numberOfIntegrationPoints):
        tags = set(listOfTags[i]+["ALLELEMENT"])
        tagsIntersec = keysConstitutiveLaws & tags
        assert len(tagsIntersec) == 1, "either no constitutive law has been set or there are more than one constitutive law for a reducedIntegrationPoint"
        materialKeyPerIntegrationPoint.append(tagsIntersec.pop())

    return materialKeyPerIntegrationPoint


def CellDataToIntegrationPointsData(mesh, scalarFields, set = None, relativeDimension = 0):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.CellDataToIntegrationPointsData(unstructuredMesh, scalarFields, set, relativeDimension)


def IntegrationPointsToCellData(mesh, scalarFields):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.IntegrationPointsToCellData(unstructuredMesh, scalarFields)


def ConvertMeshToUnstructuredMesh(mesh):

    if isinstance(mesh, BTUM.BasicToolsUnstructuredMesh) == False:
        """from BasicTools.Containers import UnstructuredMesh as UM
        unstructuredMesh = UM.UnstructuredMesh()
        unstructuredMesh.nodes = mesh.GetNodes()
        cpt = 0
        for name,coon in mesh.AllElementsIterator():
            eledata = mesh.elements.GetElementOfType(name)
            eledata.AddElementUsingOriginalId(coon,cpt)
            cpt += 1
        unstructuredMesh.PrepareForOutput()"""
        pass  # pragma: no cover
    else:
        unstructuredMesh = mesh.GetInternalStorage()

    return unstructuredMesh


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
