# -*- coding: utf-8 -*-
import numpy as np

from MordicusCore.IO.WriterBase import WriterBase
from MordicusCore.Containers.CompressedFormats import CompressedFormatsBase
from BasicTools.IO import XdmfWriter as XW
from MordicusModules.safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
from MordicusModules.safran.Containers.Meshes import MeshTools as MT


def WritePXDMF(mesh, compressedSnapshots, outputName=None):
    """
    Functional API
    
    Writes a solution on disk satisfying the corresponding format

    Parameters
    ----------
    mesh : MeshBase
        the geometric support of the solution from one of the formats defined in Containers.Meshes
    compressedSnapshots : CompressedFormatsBase
        compressed solution to write on disk
    outputName : str, optional
        name of the file on disk where the solution is written
    """
    writer = PXDMFWriter(outputName)
    writer.Write(mesh, compressedSnapshots)


class PXDMFWriter(WriterBase):
    """
    Class containing the PXDMF writer
    """

    def __init__(self, outputName=None):
        super(PXDMFWriter, self).__init__(outputName)

    def Write(self, mesh, compressedSnapshots):
        """
        Writes a solution on disk in the PXDMF format.
        
        Optimal input mesh format is BasicToolsUnstructuredMesh.
        
        Parameters
        ----------
        mesh : MeshBase
            the geometric support of the solution from one of the formats defined in Containers.Meshes
        solution : CompressedFormatsBase
            object to write on disk
        """

        assert isinstance(
            compressedSnapshots, CompressedFormatsBase.CompressedFormatsBase
        ), "compressedSnapshots must be an instance of an object inheriting from Containers.CompressedFormatsBase"

        unstructuredMesh = MT.ConvertMeshToUnstructuredMesh(mesh)

        if self.outputName is None:
            self.outputName = compressedSnapshots.GetName() + "_compressed"

        writer = XW.XdmfWriter()
        writer.SetFileName(None)
        writer.SetXmlSizeLimit(0)
        writer.SetBinary(True)
        writer.SetParafac(True)
        writer.Open(filename=self.outputName + ".pxdmf")

        from BasicTools.Containers import UnstructuredMeshTools as UMT
        import BasicTools.Containers.ElementNames as ElementNames

        n = compressedSnapshots.GetNumberOfSnapshots()
        numberOfModes = compressedSnapshots.GetNumberOfModes()
        a = np.arange(n)

        points = np.zeros((n, 2))
        points[:, 0] = compressedSnapshots.GetTimes()

        bars = np.empty((n - 1, 2))
        bars[:, 0] = a[:-1]
        bars[:, 1] = a[1:]

        meshT = UMT.CreateMeshOf(points, bars, ElementNames.Bar_2)

        meshT.props["ParafacDims"] = 1
        meshT.props["ParafacDim0"] = "t"

        numberOfNodes = compressedSnapshots.GetNumberOfNodes()
        numberOfComponents = compressedSnapshots.GetNbeOfComponents()

        pointFieldsNames = []
        pointFields = []

        for i in range(numberOfModes):
            pointFields.append(
                np.array(
                    [
                        np.array(
                            compressedSnapshots.GetCoefficients()[:, i],
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
            data = np.array(compressedSnapshots.GetModes()[i, :], dtype=np.float32)
            data.shape = (numberOfComponents, numberOfNodes)
            pointFields.append(data.T)
            pointFieldsNames.append(self.outputName + "_" + str(i))
        writer.Write(
            unstructuredMesh, PointFields=pointFields, PointFieldsNames=pointFieldsNames
        )
        writer.Close()
