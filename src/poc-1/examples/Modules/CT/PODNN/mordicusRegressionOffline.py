from Mordicus.Modules.CT.IO import MeshReader as MR
from Mordicus.Modules.CT.IO import VTKSolutionReader as VSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD
#from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Modules.CT.OperatorCompressors import Regression
import numpy as np
import os


def test():

    print('Read mesh')
    mesh = MR.ReadMesh("meshBase.vtu")
    numberOfNodes = mesh.GetNumberOfNodes()
    print('Read VTK base file')
    VTKBase = MR.ReadVTKBase("meshBase.vtu")
    #solutionName = "Mach"
    solutionName = "Pression"
    print('solutionName ', solutionName)
    nbeOfComponents = 1
    primality = True

    collectionProblemData = CPD.CollectionProblemData()

    parameters = [[4.0], [4.25]]   ###two parameters

    for i in range(len(parameters)):
        folder = "Computation" + str(i) + "/"

        outputTimeSequence = np.arange(0., 11)

        solution = S.Solution(
            solutionName=solutionName,
            nbeOfComponents=nbeOfComponents,
            numberOfNodes=numberOfNodes,
            primality=primality,
        )

        problemData = PD.ProblemData(folder)
        problemData.AddSolution(solution)

        solutionReader = VSR.VTKSolutionReader(
                solution.GetSolutionName()
        )

        count=0
        for t in outputTimeSequence:
            print('\ntime   ', t)
            solutionFileName = folder + "cylinder_"
            
            snapshot = solutionReader.npRead(
                solutionFileName, count
            )
            solution.AddSnapshot(snapshot, t)
            problemData.AddParameter(np.array(parameters[i]), t)
            print('Data      ' , solutionFileName, int(t))
            print('Parameters' , problemData.GetParameters().get(t))
            count +=1

        collectionProblemData.AddProblemData(problemData)
    

    print("\nSolutions have been read\n")

    ##################################################
    # OFFLINE
    ##################################################

    reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
        collectionProblemData, solutionName, 1.0e-4
    )

    collectionProblemData.AddReducedOrderBasis(solutionName, reducedOrderBasis)
    print("A reduced order basis has been computed has been constructed using SnapshotPOD")

    collectionProblemData.CompressSolutions(solutionName)
    print("The solution has been compressed")

    Regression.CompressOperator(
        collectionProblemData, solutionName
    )

    collectionProblemData.SaveState("mordicusState")


    ###write POD modes
    from Mordicus.Modules.CT.IO import numpyToVTKWriter as NTV
    numpyToVTK = NTV.VTKWriter(VTKBase)
    numpyToVTK.numpyToVTKPODWrite(solutionName, reducedOrderBasis)


    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
