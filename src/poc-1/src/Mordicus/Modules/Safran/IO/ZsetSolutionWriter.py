# -*- coding: utf-8 -*-
import numpy as np

from BasicTools.IO import UtWriter as UW
from BasicTools.FE import FETools as FT
from BasicTools.Containers import Filters
from BasicTools.FE.IntegrationsRules import Lagrange as Lagrange

from mpi4py import MPI
from pathlib import Path
import os


primalSolutionComponents = {1:[""], 2:["1", "2"], 3:["1", "2", "3"]}


def WriteZsetSolution(mesh, meshFileName, solutionFileName, collectionProblemData, onlineProblemData, solutionNameRef):


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

    coef = {}
    nNodeVar = 0
    nIntegVar = 0
    for name, solution in onlineProblemData.solutions.items():
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

    arange = np.arange(nbIntegPoints)


    numberElements = []
    nbPtIntPerElement = []


    ff = Filters.ElementFilter(mesh.GetInternalStorage())
    ff.SetDimensionality(mesh.GetInternalStorage().GetDimensionality())
    for name,data,ids in ff:
        p,w =  Lagrange(name)
        numberElements.append(data.GetNumberOfElements())
        nbPtIntPerElement.append(len(w))

    nbTypeEl = len(numberElements)


    timeSequence = onlineProblemData.GetSolution(solutionNameRef).GetTimeSequenceFromCompressedSnapshots()

    nbDofs = onlineProblemData.GetSolution(solutionNameRef).GetNumberOfDofs()


    count = 0
    for time in timeSequence:
        resFile.write(str(count+1)+" "+str(count)+" "+str(1)+" "+str(1)+" "+str(time)+"\n")

        resNode  = np.empty(nNodeVar*nbDofs)
        fieldInteg = np.empty((nIntegVar,nbIntegPoints))
        resInteg = np.empty(nIntegVar*nbIntegPoints)

        countNode = 0
        countInteg = 0

        for name, solution in onlineProblemData.solutions.items():

            res = np.dot(solution.GetCompressedSnapshotsAtTime(time), collectionProblemData.GetReducedOrderBasis(name))

            if solution.primality == True:
                resNode[countNode*nbDofs:(countNode+1)*nbDofs] = res
                countNode += 1
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

