# -*- coding: utf-8 -*-
from BasicTools.FE import FETools as FT
from BasicTools.Containers import Filters
from BasicTools.FE.IntegrationsRules import Lagrange as Lagrange
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


def ComputeFEInterpMatAtGaussPoint(mesh):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeFEInterpMatAtGaussPoint(unstructuredMesh)


def ComputeFEInterpGradMatAtGaussPoint(mesh):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeFEInterpGradMatAtGaussPoint(unstructuredMesh)


def ComputeMecaIntegrator(mesh, elementSet = "ALLELEMENT"):

    unstructuredMesh = ConvertMeshToUnstructuredMesh(mesh)

    return FT.ComputeMecaIntegrator(unstructuredMesh)



"""def ComputeMecaIntegrator2(mesh, reducedOrderBasis):


    mesh = ConvertMeshToUnstructuredMesh(mesh)

    nbNodes = mesh.GetNumberOfNodes()
    dimension = mesh.GetDimensionality()

    ff = Filters.ElementFilter(mesh)
    ff.SetDimensionality(dimension)

    spaces, numberings, offset, NGauss = FT.PrepareFEComputation(mesh, ff, dimension)

    integrationWeights = np.zeros(NGauss)

    convInd = {1:[0], 2:[0, 2, 2, 1], 3:[0, 3, 4, 3, 1, 5, 4, 5, 2]}
    nbeInd  = {1:1, 2:3, 3:6}

    Bphi = np.zeros((nbModes,NGauss))
    Bphiphi = np.zeros((nbModes,nbModes,NGauss))

    count = 0
    for name,data,ids in ff:
        p,w =  Lagrange(name)

        nbsf = spaces[name].GetNumberOfShapeFunctions()
        ones = np.ones(dimension*nbsf,dtype=int)

        B = np.zeros((dimension*nbsf

        for el in ids:

            xcoor = mesh.nodes[data.connectivity[el],:]
            leftNumbering = np.concatenate([numberings[j][name][el,:]+offset[j] for j in range(dimension)])

            for ip in range(len(w)):
                Jack, Jdet, Jinv = spaces[name].GetJackAndDetI(ip,xcoor)
                BxByBzI = Jinv(spaces[name].valdphidxi[ip])

                integrationWeights[count] = w[ip]*Jdet

                for i in range(nbsf):
                    for k in range(dimension):
                        for l in range(dimension):
                            B[i+l*nbsf, convInd[dimension][k*dimension + l]] = BxByBzI[k,i]

                dat.extend((B.T).ravel())
                for i in range(nbeInd[dimension]):
                    row.extend(leftNumbering.ravel())
                    col.extend(ones*(nbeInd[dimension]*count+i))

                count += 1

    dat = np.array(dat)
    row = np.array(row)
    col = np.array(col)


    integrator = coo_matrix((dat, (row, col)), shape=(dimension*nbNodes,nbeInd[dimension]*NGauss)).tocsr()

    return integrationWeights, integrator


    nbModes = reducedOrderBasis.shape[0]
    dim     = mesh.GetDimensionality()

    ff = Filters.ElementFilter(mesh)
    ff.SetDimensionality(dim)

    spaces, numberings, offset, NGauss = FT.PrepareFEComputation(mesh, ff)

    gradgrad = np.zeros((nbModes,nbModes,NGauss))
    phi = np.zeros((nbModes,NGauss))
    phiphi = np.zeros((nbModes,nbModes,NGauss))

    count = 0
    for name,data,ids in ff:
        p,w =  Lagrange(name)

        lenNumbering = len(numberings[0][name][0,:])

        for el in ids:

            xcoor = mesh.nodes[data.connectivity[el],:]
            leftNumberings = numberings[0][name][el,:]+offset[0]

            m = reducedOrderBasis[:,leftNumberings[:]]

            for ip in range(len(w)):
                Jack, Jdet, Jinv = spaces[name].GetJackAndDetI(ip,xcoor)
                BxByBzI = Jinv(spaces[name].valdphidxi[ip])

                left = spaces[name].valN[ip]
                prod = np.tensordot(BxByBzI,BxByBzI, axes=(0,0))

                localPhi = np.dot(m, left)
                phi[:,count] = localPhi
                phiphi[:,:,count] = np.outer(localPhi, localPhi)
                gradgrad[:,:,count] += np.dot(m, np.dot(prod, m.T))

                count += 1

    return gradgrad, phi, phiphi"""




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
