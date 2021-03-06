# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from mpi4py import MPI

from BasicTools.IO import XdmfWriter as XW
from Mordicus.Modules.Safran.FE import FETools as FT


def WriteCompressedSolution(mesh, compressedSnapshots, reducedOrderBasis, outputName):
    """
    Functional API

    Writes a solution on disk from the compressed snapshots

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    compressedSnapshots : dict
        dictionary with time indices as keys and a np.ndarray of size
        (numberOfModes,) containing the coefficients of the reduced solution
    reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
    outputName : str
        name of the file on disk where the solution is written
    """
    writer = PXDMFWriter(outputName)
    writer.Write(mesh, compressedSnapshots, reducedOrderBasis)


def WriteReducedOrderBasis(mesh, reducedOrderBasis, outputName):
    """
    Functional API

    Writes a reduced order basis on disk

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
    outputName : str
        name of the file on disk where the solution is written
    """
    indices = {}
    euclideanBasis = np.eye(reducedOrderBasis.shape[0])

    for i in range(reducedOrderBasis.shape[0]):
        indices[float(i)] = euclideanBasis[i]

    writer = PXDMFWriter(outputName)
    writer.Write(mesh, indices, reducedOrderBasis)


def WriteSolution(mesh, solution, reducedOrderBasis):
    """
    Functional API

    Writes a solution on disk

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    solution : Solution
        solution containing compressedSnapshots
    reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
    """
    writer = PXDMFWriter(solution.GetSolutionName())
    writer.Write(mesh, solution.GetCompressedSnapshots(), reducedOrderBasis)


class PXDMFWriter(object):
    """
    Class containing the PXDMF writer

    Attributes
    ----------
    outputName : str
        name of the file to be written on disk
    """

    def __init__(self, outputName):

        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
            outputName += "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3)

        self.outputName = outputName


    def Write(self, mesh, compressedSnapshots, reducedOrderBasis):
        """
        Writes a solution on disk in the PXDMF format.

        Parameters
        ----------
        mesh : BasicToolsUnstructuredMesh
            high-dimensional mesh
        compressedSnapshots : dict
            dictionary with time indices as keys and a np.ndarray of size
            (numberOfModes) containing the coefficients of the reduced solution
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """

        assert isinstance(compressedSnapshots, dict)

        if MPI.COMM_WORLD.Get_size() > 1:  # pragma: no cover
            #ATTENTION: BasicTools Xdmf writer not supported in parallel
            import pickle
            with open(self.outputName+'.pickle', 'wb') as handle:
                pickle.dump([compressedSnapshots, reducedOrderBasis], handle, protocol=pickle.HIGHEST_PROTOCOL)

        else:

            unstructuredMesh = FT.ConvertMeshToUnstructuredMesh(mesh)

            writer = XW.XdmfWriter()
            writer.SetFileName(None)
            writer.SetXmlSizeLimit(0)
            writer.SetBinary(True)
            writer.SetParafac(True)
            writer.Open(filename=self.outputName + ".pxdmf")

            from BasicTools.Containers import UnstructuredMeshCreationTools as UMT
            import BasicTools.Containers.ElementNames as ElementNames

            n = len(compressedSnapshots.keys())
            numberOfModes = reducedOrderBasis.shape[0]
            a = np.arange(n)

            points = np.zeros((n, 2))
            points[:, 0] = list(compressedSnapshots.keys())

            bars = np.empty((n - 1, 2))
            bars[:, 0] = a[:-1]
            bars[:, 1] = a[1:]

            meshT = UMT.CreateMeshOf(points, bars, ElementNames.Bar_2)

            meshT.props["ParafacDims"] = 1
            meshT.props["ParafacDim0"] = "t"

            numberOfNodes = mesh.GetNumberOfNodes()
            numberOfComponents = reducedOrderBasis.shape[1]//numberOfNodes

            pointFieldsNames = []
            pointFields = []

            coefficients = np.array(list(compressedSnapshots.values()))

            for i in range(numberOfModes):
                pointFields.append(
                    np.array(
                        [
                            np.array(
                                coefficients[:,i],
                                dtype=np.float32,
                            )
                        ]
                        * numberOfComponents
                    ).T
                )
                pointFieldsNames.append(self.outputName + "_" + str(i))
            writer.Write(meshT, PointFields=pointFields, PointFieldsNames=pointFieldsNames)

            unstructuredMesh.props["ParafacDims"] = unstructuredMesh.GetDimensionality()

            physComponents = ["x", "y", "z"]
            for i in range(unstructuredMesh.GetDimensionality()):
                unstructuredMesh.props["ParafacDim" + str(i)] = physComponents[i]

            pointFieldsNames = []
            pointFields = []

            for i in range(numberOfModes):
                data = np.array(reducedOrderBasis[i, :], dtype=np.float32)
                data.shape = (numberOfComponents, numberOfNodes)
                pointFields.append(data.T)
                pointFieldsNames.append(self.outputName + "_" + str(i))

            writer.Write(unstructuredMesh, PointFields=pointFields,
                         PointFieldsNames=pointFieldsNames)
            writer.Close()


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


