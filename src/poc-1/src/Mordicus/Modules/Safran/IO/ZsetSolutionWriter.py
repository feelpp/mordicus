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

from BasicTools.FE import FETools as FT
from BasicTools.Containers import Filters
from BasicTools.FE.IntegrationsRules import LagrangeIsoParam

from mpi4py import MPI
from pathlib import Path


primalSolutionComponents = {1:[""], 2:["1", "2"], 3:["1", "2", "3"]}


def WriteZsetSolution(mesh, meshFileName, solutionFileName,\
                      collectionProblemData, problemData, solutionNameRef = None,\
                      timeSequence = None, outputReducedOrderBasis = False):
    """
    Writes a solution from compressedSnapshots or a reducedOrderBases on disk
    satisfying the Z-set format

    Parameters
    ----------
    mesh : BasicToolsUnstructuredMesh
        high-dimensional mesh
    meshFileName : str
        name of the meshfile already available on disk
    solutionFileName : str
        name of the file on disk where the solution is written
    collectionProblemData : CollectionProblemData
        collectionProblemData containing the reducedOrderBases to write
    problemData : ProblemData
        problemData containing the compressedSnapshots to write
    solutionNameRef : str, option
        name of the solution used to define the timeSequence
    timeSequence : list or 1D np.ndarray, optional
        not used for writing reducedOrderBases, if None for writing a solution,
        the time sequences defined in compressedSnapshots is used (in that
        case, solutionNameRef must me defined)
    outputReducedOrderBasis : bool, optional
        True to write reducedOrderBases, False to write solutions

    Notes
    -----
        In the current implementations, all reduced order basis are written in
        a Zset-like format with the rank of the modes as the "time": the fields
        having less than the max number of modes have their last modes repeated
    """

    if outputReducedOrderBasis:
        nameList = list(collectionProblemData.reducedOrderBases.keys())
    else:
        tempList = list(problemData.solutions.keys())
        nameList = [n for n in tempList if problemData.solutions[n].GetCompressedSnapshots()]


    folder = str(Path(solutionFileName).parents[0])
    suffix = str(Path(solutionFileName).suffix)
    stem = str(Path(solutionFileName).stem)

    folderMesh = str(Path(meshFileName).parents[0])
    suffixMesh = str(Path(meshFileName).suffix)
    stemMesh = str(Path(meshFileName).stem)

    if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
        solutionFileName = folder + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        meshFileName = folderMesh + os.sep + stemMesh + "-pmeshes" + os.sep + stemMesh + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffixMesh

    __string = u"**meshfile "+meshFileName+"\n"

    __stringNode = "**node "
    __stringInteg = "**integ "


    nNodeVar = 0
    nIntegVar = 0
    maxNumberOfModes = 0

    for name in nameList:
        solution = problemData.GetSolution(name)

        if outputReducedOrderBasis:
            maxNumberOfModes = max(maxNumberOfModes, collectionProblemData.GetReducedOrderBasis(name).shape[0])

        if solution.primality == True:
            for component in primalSolutionComponents[solution.GetNbeOfComponents()]:
                __stringNode += solution.solutionName+component+" "
                nNodeVar += 1
        else:
            nIntegVar += 1
            __stringInteg += solution.solutionName+" "

    __stringNode += "\n"
    __stringInteg += "\n"

    __string += __stringNode
    __string += __stringInteg

    __string += "**element\n"

    for ff in [".node",".ctnod",".integ", ".ut", ".cut"]:
        try:
            os.remove(solutionFileName+ff)
        except OSError:
            pass

    resFile = open(solutionFileName+".ut", "a")
    resFileNode = open(solutionFileName+".node", "a")
    resFileInteg = open(solutionFileName+".integ", "a")


    resFile.write(__string)


    spaces, numberings, offset, nbIntegPoints = FT.PrepareFEComputation(mesh.GetInternalStorage())


    numberElements = []
    nbPtIntPerElement = []


    ff = Filters.ElementFilter(mesh.GetInternalStorage())
    ff.SetDimensionality(mesh.GetInternalStorage().GetDimensionality())
    for name,data,ids in ff:
        p,w =  LagrangeIsoParam[name]
        numberElements.append(data.GetNumberOfElements())
        nbPtIntPerElement.append(len(w))

    nbTypeEl = len(numberElements)


    if outputReducedOrderBasis:
        timeSequence = np.arange(maxNumberOfModes)
    elif timeSequence == None:
        assert solutionNameRef != None, "solutionNameRef must be specified"
        timeSequence = problemData.GetSolution(solutionNameRef).GetTimeSequenceFromCompressedSnapshots()


    #nbDofs = problemData.GetSolution(solutionNameRef).GetNumberOfDofs()
    nbNodes = mesh.GetNumberOfNodes()


    count = 0
    for time in timeSequence:
        resFile.write(str(count+1)+" "+str(count)+" "+str(1)+" "+str(1)+" "+str(time)+"\n")

        resNode  = np.empty(nNodeVar*nbNodes)
        fieldInteg = np.empty((nIntegVar,nbIntegPoints))
        resInteg = np.empty(nIntegVar*nbIntegPoints)

        countNode = 0
        countInteg = 0


        for name in nameList:
            solution = problemData.GetSolution(name)

            if outputReducedOrderBasis:
                locTime = min(time, collectionProblemData.GetReducedOrderBasis(name).shape[0]-1)
                res = collectionProblemData.GetReducedOrderBasis(name)[locTime]

            else:
                res = np.dot(solution.GetCompressedSnapshotsAtTime(time), collectionProblemData.GetReducedOrderBasis(name))

            if solution.primality == True:
                loccountNode = 0
                for c in range(solution.GetNbeOfComponents()):
                    resNode[countNode*nbNodes:(countNode+1)*nbNodes] = res[loccountNode*nbNodes:(loccountNode+1)*nbNodes]
                    countNode += 1
                    loccountNode += 1
            else:
                fieldInteg[countInteg,:] = res
                countInteg += 1

        resNode.astype(np.float32).byteswap().tofile(resFileNode)

        count0 = 0
        for l in range(nbTypeEl):
            for m in range(numberElements[l]):
                for k in range(nIntegVar):
                    resInteg[count0:count0+nbPtIntPerElement[l]] = fieldInteg[k,nbPtIntPerElement[l]*m:nbPtIntPerElement[l]*m+nbPtIntPerElement[l]]
                    count0 += nbPtIntPerElement[l]
        resInteg.astype(np.float32).byteswap().tofile(resFileInteg)

        count += 1


    resFile.close()
    resFileNode.close()
    resFileInteg.close()


    if MPI.COMM_WORLD.Get_size() > 1 and MPI.COMM_WORLD.Get_rank() == 0:# pragma: no cover
        globalMeshFileName = folderMesh + os.sep + stemMesh + suffixMesh
        globalSolutionFileName = folder + os.sep + stem + suffix
        __string = "***decomposition\n**global_mesh "+globalMeshFileName+"\n**domains "+str(MPI.COMM_WORLD.Get_size())+"\n"
        with open(globalSolutionFileName+".cut", "w") as f:
            f.write(__string)
        f.close()


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
