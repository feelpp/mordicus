from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.CT.IO import MeshReader as MR
import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)



    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################
    VTKBase = MR.ReadVTKBase("meshBase.vtu")
    mesh = MR.ReadMesh("meshBase.vtu")
    solutionName = "Mach"
    numberOfNodes = mesh.GetNumberOfNodes()
    nbeOfComponents = 1
    primality = True

    collectionProblemData = CPD.LoadState("mordicusState")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBasis = collectionProblemData.reducedOrderBases[solutionName]

    ##################################################
    # ONLINE
    ##################################################
    onlineProblemData = PD.ProblemData("Online")

    OnlineTimeSequence = np.array(np.arange(0, 1, 10), dtype=float)

    for t in OnlineTimeSequence:
        onlineProblemData.AddParameter(np.array([0.3, 8.0]), t)


    compressedSnapshots = Regression.ComputeOnline(
        onlineProblemData, operatorCompressionData
    )


    PW.WritePXDMF(mesh, compressedSnapshots, reducedOrderBasis, solutionName)
    print("The compressed solution has been written in PXDMF Format")


    solution = S.Solution(
        solutionName=solutionName,
        nbeOfComponents=nbeOfComponents,
        numberOfNodes=numberOfNodes,
        primality=primality,
    )
    onlineProblemData.AddSolution(solution)

    onlineProblemData.solutions[solutionName].SetCompressedSnapshots(compressedSnapshots)
    solution.UncompressSnapshots(reducedOrderBasis)


    ###write Rec. Solution
    from Mordicus.Modules.CT.IO import numpyToVTKWriter as NTV
    numpyToVTK = NTV.VTKWriter(VTKBase)
    numpyToVTK.numpyToVTKSanpWrite(solutionName, solution.GetSnapshotsList())

    os.chdir(initFolder)

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
