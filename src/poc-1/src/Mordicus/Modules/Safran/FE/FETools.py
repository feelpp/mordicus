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
    thermal in any dimension. (Lagrange isoparametric finite elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
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
    Computes the H10 scalar product used to compute the correlations
    between the primal solution snapshots. The numberOfComponents
    depends on the solution type: 3 for solid mechanics in 3D, or 1 for
    thermal in any dimension. (Lagrange isoparametric finite elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
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
    """
    Computes determinant of the Jacobian of the transformation of the
    transformation between the reference element and the mesh element, at
    the integration points. (Lagrange isoparametric finite elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    elementSets : list of strings
        sets of elements on which the function is computed
    relativeDimension : int (0, -1 or -2)
        difference between the dimension of the elements on which the function
        is computed and the dimensionality of the mesh

    Returns
    -------
    np.ndarray
        of size (numberOfIntegrationPoints,)
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeJdetAtIntegPoint(unstructuredMesh, elementSets, relativeDimension)


def ComputePhiAtIntegPoint(mesh, elementSets = None, relativeDimension = 0):
    """
    Computes the value of the finite element shape functions at the integration
    points and the integration weights (Lagrange isoparametric finite elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    elementSets : list of strings
        sets of elements on which the function is computed
    relativeDimension : int (0, -1 or -2)
        difference between the dimension of the elements on which the function
        is computed and the dimensionality of the mesh

    Returns
    -------
    np.ndarray
        of size (numberOfIntegrationPoints,)
    scipy.sparse.coo_matrix
        of size (numberOfIntegrationPoints, numberOfModes)
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputePhiAtIntegPoint(unstructuredMesh, elementSets, relativeDimension)


def ComputeGradPhiAtIntegPoint(mesh, elementSets = None, relativeDimension = 0):
    """
    Computes the components of the gradient of the shape functions at the
    integration points and the integration weights (Lagrange isoparametric
    finite elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    elementSets : list of strings
        sets of elements on which the function is computed
    relativeDimension : int (0, -1 or -2)
        difference between the dimension of the elements on which the function
        is computed and the dimensionality of the mesh

    Returns
    -------
    np.ndarray
        of size (numberOfIntegrationPoints,)
    list
        of length dimensionality of the mesh, of scipy.sparse.coo_matrix of
        size (numberOfIntegrationPoints, numberOfModes)
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeGradPhiAtIntegPoint(unstructuredMesh, elementSets, relativeDimension)


def ComputeNormalsAtIntegPoint(mesh, elementSets = None):
    """
    Computes the normals at the elements from the sets elementSets in the
    ambiant space (i.e. if mesh is of dimensionality 3, elementSets should
    contain 2D elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    elementSets : list of strings
        sets of elements on which the function is computed

    Returns
    -------
    np.ndarray
        of size (dimensionality, numberOfIntegrationPoints)
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeNormalsAtIntegPoint(unstructuredMesh, elementSets)


def ComputeNumberOfIntegrationPoints(mesh):
    """
    Computes the number of integration points. (Lagrange isoparametric finite
    elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh

    Returns
    -------
    int
        numberOfIntegrationPoints
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)
    _, _, _, numberOfIntegrationPoints = FT.PrepareFEComputation(unstructuredMesh)

    return numberOfIntegrationPoints


def ComputeIntegrationPointsTags(mesh, dimension = None):
    """
    Returns a list of lists (of str) at each integration point (Lagrange
    isoparametric finite elements). Each list contains all the tags of the
    element of dimension "dimension" containing the considered integration
    points.

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    elementSets : list of strings
        sets of elements on which the function is computed

    Returns
    -------
    list of lists (of str)
        of length numberOfIntegrationPoints
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeIntegrationPointsTags(unstructuredMesh, dimension)


def ComputeIndicesOfIntegPointsPerMaterial(listOfTags, keysConstitutiveLaws):
    """
    From the list of lists containing all the tags of the element containing
    the integration points of the considered mesh, and the set of tags on which
    constitutive laws are defined, returns a dictionary containing the ranks of
    integration points for each tag (inverse the information contained in
    listOfTags).

    Parameters
    ----------
    listOfTags : list of lists (of str)
        of length numberOfIntegrationPoints, containing all the tags of the
        element containing the integration points
    keysConstitutiveLaws : set (of str)
        set of tags on which constitutive laws are defined

    Returns
    -------
    dict (str: np.ndarray)
        dictionary with element tags (str) as keys and ranks of integration
        points (1D np.ndarray) as values
    """
    materialKeyPerIntegrationPoint = ComputeMaterialKeyPerIntegrationPoint(listOfTags, keysConstitutiveLaws)

    numberOfIntegrationPoints = len(listOfTags)

    IndicesOfIntegPointsPerMaterial = {}
    arange = np.arange(numberOfIntegrationPoints)
    for key in keysConstitutiveLaws:
        IndicesOfIntegPointsPerMaterial[key] = arange[np.array(materialKeyPerIntegrationPoint) == key]

    return IndicesOfIntegPointsPerMaterial


def ComputeMaterialKeyPerIntegrationPoint(listOfTags, keysConstitutiveLaws):
    """
    From the list of lists containing all the tags of the element containing
    the integration points of the considered mesh, and the set of tags on which
    constitutive laws are defined, returns the list containing the unique tag
    defining the constitutive laws key at each integration point.

    Parameters
    ----------
    listOfTags : list of lists (of str)
        of length numberOfIntegrationPoints, containing all the tags of the
        element containing the integration points
    keysConstitutiveLaws : set (of str)
        set of tags on which constitutive laws are defined

    Returns
    -------
    list (of str)
        of length numberOfIntegrationPoints, containing the unique tag defining
        the constitutive laws key at each integration point
    """
    numberOfIntegrationPoints = len(listOfTags)

    materialKeyPerIntegrationPoint = []
    for i in range(numberOfIntegrationPoints):
        tags = set(listOfTags[i]+["ALLELEMENT"])
        tagsIntersec = keysConstitutiveLaws & tags
        assert len(tagsIntersec) == 1, "either no constitutive law has been set or there are more than one constitutive law for a reducedIntegrationPoint"
        materialKeyPerIntegrationPoint.append(tagsIntersec.pop())

    return materialKeyPerIntegrationPoint


def CellDataToIntegrationPointsData(mesh, scalarFields, elementSet = None, relativeDimension = 0):
    """
    Change the representation of scalarFields from data constant by cell
    (elements) to data at integration points. (Lagrange isoparametric finite
    elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    scalarFields : np.ndarray of size (nbe of fields, nbe of elements) or dict
        with "nbe of fields" as keys and np.ndarray of size (nbe of elements,) as
        values fields whose representation in changed by the function
    elementSet : elementSet defining the elements on which the function is
        computed. If None, takes all the elements of considered dimension
    relativeDimension : int (0, -1 or -2)
        difference between the dimension of the elements on which the function
        is computed and the dimensionality of the mesh

    Returns
    -------
    np.ndarray
        of size (nbe of fields, numberOfIntegrationPoints)
    """
    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.CellDataToIntegrationPointsData(unstructuredMesh, scalarFields, elementSet, relativeDimension)


def IntegrationPointsToCellData(mesh, scalarFields):
    """
    Change the representation of scalarFields from data at integration points
    to data constant by cell (elements) - taking the mean of values at the
    integration points in each elements. (Lagrange isoparametric finite
    elements)

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    scalarFields : np.ndarray of size (nbe of fields, nbe of elements) or dict
        with "nbe of fields" as keys and np.ndarray of size (nbe of elements,) as
        values fields whose representation in changed by the function

    Returns
    -------
    np.ndarray
        of size (nbe of elements,)
    """
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
