# -*- coding: utf-8 -*-
from BasicTools.FE import FETools as FT
from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM


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


def ComputeFEInterpMatAtGaussPoint(mesh):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeFEInterpMatAtGaussPoint(unstructuredMesh)


def ComputeFEInterpGradMatAtGaussPoint(mesh):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeFEInterpGradMatAtGaussPoint(unstructuredMesh)


def ComputeMecaIntegrator(mesh, elementSet = "ALLELEMENT"):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeMecaIntegrator(unstructuredMesh)


def ComputeNumberOfIntegrationPoints(mesh):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)
    _, _, _, numberOfIntegrationPoints = FT.PrepareFEComputation(unstructuredMesh)

    return numberOfIntegrationPoints


def IntegrateVectorNormalComponentOnSurface(mesh, set, vector):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    assembledVector = FT.IntegrateVectorNormalComponentOnSurface(unstructuredMesh, set, vector)

    return assembledVector


def ComputeIntegrationPointsTags(mesh, dimension):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeIntegrationPointsTags(unstructuredMesh, dimension)


def IntegrateCentrifugalEffect(mesh, density, direction, center):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.IntegrateCentrifugalEffect(unstructuredMesh, density, direction, center)


def IntegrateOrderOneTensorOnSurface(mesh, set, orderOneTensor):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.IntegrateOrderOneTensorOnSurface(unstructuredMesh, set, orderOneTensor)


def IntegrateOrderTwoTensorOnSurface(mesh, set, orderTwoTensor):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.IntegrateOrderTwoTensorOnSurface(unstructuredMesh, set, orderTwoTensor)




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
