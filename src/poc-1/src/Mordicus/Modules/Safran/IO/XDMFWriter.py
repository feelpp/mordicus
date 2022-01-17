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

from BasicTools.IO import XdmfWriter as XW
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.IO import StateIO as SIO
import numpy as np


def WriteReducedOrderBases(mesh, problemData, reducedOrderBases, outputName):
    """
    Functional API

    Writes a solution on disk satisfying the corresponding format

    Parameters
    ----------
    mesh : MeshBase
        the geometric support of the solution from one of the formats defined in Containers.Meshes
    compressedSnapshots : dict
        dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
    reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
    outputName : str, optional
        name of the file on disk where the solution is written
    """


    writer = XDMFWriter(outputName)
    writer.WriteReducedOrderBases(mesh, problemData, reducedOrderBases)


def WriteSolution(mesh, solution, outputName):
    """
    Functional API

    Writes a solution on disk satisfying the corresponding format

    Parameters
    ----------
    mesh : MeshBase
        the geometric support of the solution from one of the formats defined in Containers.Meshes
    solution : Solution
        solution containing compressedSnapshots
    reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
    outputName : str, optional
        name of the file on disk where the solution is written
    """
    writer = XDMFWriter(outputName)
    writer.WriteSolution(mesh, solution)


def WriteProblemDataSolutions(mesh, problemData, solutionNameRef, outputName):
    """
    Functional API

    Writes a solution on disk satisfying the corresponding format

    Parameters
    ----------
    mesh : MeshBase
        the geometric support of the solution from one of the formats defined in Containers.Meshes
    solution : Solution
        solution containing compressedSnapshots
    reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
    outputName : str, optional
        name of the file on disk where the solution is written
    """
    writer = XDMFWriter(outputName)
    writer.WriteProblemDataSolutions(mesh, problemData, solutionNameRef)



class XDMFWriter(object):
    """
    Class containing the PXDMF writer
    """

    def __init__(self, outputName):

        self.outputName = outputName


    def WriteSolution(self, mesh, solution):
        """
        Writes a solution on disk in the PXDMF format.

        Optimal input mesh format is BasicToolsUnstructuredMesh.

        Parameters
        ----------
        mesh : MeshBase
            the geometric support of the solution from one of the formats defined in Containers.Meshes
        compressedSnapshots : dict
            dictionary with time indices as keys and a np.ndarray of size (numberOfModes,) containing the coefficients of the reduced solution
        reducedOrderBasis : np.ndarray
            of size (numberOfModes, numberOfDOFs)
        """

        if MPI.COMM_WORLD.Get_size() > 1:  # pragma: no cover
            #ATTENTION: BasicTools Xdmf writer not supported in parallel
            SIO.SaveState(self.outputName, solution)

        else:

            unstructuredMesh = FT.ConvertMeshToUnstructuredMesh(mesh)

            writer = XW.XdmfWriter(self.outputName+'.xmf')
            writer.SetTemporal(True)
            writer.SetBinary(True)
            writer.Open()

            timeSequence = solution.GetTimeSequenceFromSnapshots()

            for time in timeSequence:

                pointFields = []
                pointFieldsNames = []
                cellFields = []
                cellFieldsNames = []

                data = solution.GetSnapshotAtTime(time).reshape(solution.GetNbeOfComponents(),-1)
                name = solution.GetSolutionName()

                if solution.GetPrimality() == True:
                    pointFields.append(data.T)
                    pointFieldsNames.append(name)
                else:
                    dataAtCells = FT.IntegrationPointsToCellData(mesh, data)
                    cellFields.append(np.array(dataAtCells))
                    cellFieldsNames.append(name)

                writer.Write(unstructuredMesh,PointFields=pointFields, PointFieldsNames=pointFieldsNames,
                     CellFields=cellFields, CellFieldsNames=cellFieldsNames, Time=time)

            writer.Close()


    def WriteProblemDataSolutions(self, mesh, problemData, solutionNameRef):
        """
        Writes a solution on disk in the PXDMF format.
        """

        if MPI.COMM_WORLD.Get_size() > 1:  # pragma: no cover
            #ATTENTION: BasicTools Xdmf writer not supported in parallel
            SIO.SaveState("problemData_"+self.outputName, problemData)

        else:

            unstructuredMesh = FT.ConvertMeshToUnstructuredMesh(mesh)

            writer = XW.XdmfWriter(self.outputName+'.xmf')
            writer.SetTemporal(True)
            writer.SetBinary(True)
            writer.Open()

            timeSequence = problemData.GetSolution(solutionNameRef).GetTimeSequenceFromSnapshots()

            for time in timeSequence:
                pointFields = []
                pointFieldsNames = []
                cellFields = []
                cellFieldsNames = []
                for solution in problemData.GetSolutions().values():
                    data = solution.GetSnapshotAtTime(time).reshape(solution.GetNbeOfComponents(),-1)
                    if solution.GetPrimality() == True:
                        pointFields.append(data.T)
                        pointFieldsNames.append(solution.GetSolutionName())
                    else:
                        dataAtCells = FT.IntegrationPointsToCellData(mesh, data)
                        cellFields.append(np.array(dataAtCells))
                        cellFieldsNames.append(solution.GetSolutionName())
                writer.Write(unstructuredMesh,PointFields=pointFields, PointFieldsNames=pointFieldsNames,
                             CellFields=cellFields, CellFieldsNames=cellFieldsNames, Time=time)
            writer.Close()



    def WriteReducedOrderBases(self, mesh, problemData, reducedOrderBases):
        """
        Writes a solution on disk in the PXDMF format.
        """

        if MPI.COMM_WORLD.Get_size() > 1:  # pragma: no cover
            #ATTENTION: BasicTools Xdmf writer not supported in parallel
            SIO.SaveState(self.outputName, reducedOrderBases)

        else:

            unstructuredMesh = FT.ConvertMeshToUnstructuredMesh(mesh)

            writer = XW.XdmfWriter(self.outputName+'.xmf')
            writer.SetTemporal(False)
            writer.SetBinary(True)
            writer.Open()

            pointFields = []
            pointFieldsNames = []
            cellFields = []
            cellFieldsNames = []
            for solution in problemData.GetSolutions().values():
                ROB = reducedOrderBases[solution.GetSolutionName()]
                if solution.GetPrimality() == True:
                    for i in range(ROB.shape[0]):
                        vectROB = ROB[i].reshape(solution.GetNbeOfComponents(),-1).T
                        pointFields.append(vectROB)
                        pointFieldsNames.append("ROB_"+solution.GetSolutionName()+"_"+str(i))
                else:
                    ROBAtCells = FT.IntegrationPointsToCellData(mesh, ROB)
                    for i in range(ROB.shape[0]):
                        cellFields.append(ROBAtCells[i])
                        cellFieldsNames.append("ROB_"+solution.GetSolutionName()+"_"+str(i))
            writer.Write(unstructuredMesh,PointFields=pointFields, PointFieldsNames=pointFieldsNames,
                         CellFields=cellFields, CellFieldsNames=cellFieldsNames)
            writer.Close()




if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


