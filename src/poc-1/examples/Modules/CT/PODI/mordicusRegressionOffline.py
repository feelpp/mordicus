from Mordicus.Modules.CT.IO import MeshReader as MR
from Mordicus.Modules.CT.IO import VTKSolutionReader as VSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD
from Mordicus.Core.OperatorCompressors import Regression
import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)

    
    print('Read mesh')
    mesh = MR.ReadMesh("meshBase.vtu")
    numberOfNodes = mesh.GetNumberOfNodes()
    print('Read VTK base file')
    VTKBase = MR.ReadVTKBase("meshBase.vtu")
    solutionName = "Mach"
    print('solutionName ', solutionName)
    #solutionName = "Pression"
    nbeOfComponents = 1
    primality = True

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.defineVariabilityAxes(['mu1', 'mu2'], 
                                                [float, float],
                                                [('Quantity 1', 'unit1'), ('Quantity 2', 'unit2')],
                                                ['description 1', 'description 2'])

    parameters = [[0.3, 0.0], [0.3, 15.0], [0.8, 0.0], [0.8, 15.0]]   ###two parameters

    for i in range(4):
        folder = "Computation" + str(i + 1) + "/"

        outputTimeSequence = [0.]

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
            solutionFileName = folder + "fields_"
            
            #snapshot = solutionReader.VTKReadToNp(
            snapshot = solutionReader.npRead(
                solutionFileName, count
            )
            solution.AddSnapshot(snapshot, t)
            problemData.AddParameter(np.array(parameters[i]), t)
            print('Data      ' , solutionFileName)
            print('Parameters' , problemData.GetParameters().get(t))
            count +=1

        collectionProblemData.AddProblemData(problemData, mu1=parameters[i][0], mu2=parameters[i][1])
    

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

    from sklearn.gaussian_process.kernels import WhiteKernel, RBF
    from sklearn.gaussian_process import GaussianProcessRegressor

    kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(
        noise_level=1, noise_level_bounds=(1e-10, 1e1)
    )
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)


    Regression.CompressOperator(
        collectionProblemData, solutionName, gpr
    )

    collectionProblemData.SaveState("mordicusState")


    os.chdir(initFolder)    

    ###write POD modes
    from Mordicus.Modules.CT.IO import numpyToVTKWriter as NTV
    numpyToVTK = NTV.VTKWriter(VTKBase)
    numpyToVTK.numpyToVTKPODWrite(solutionName, reducedOrderBasis)

    for _, problemData in collectionProblemData.GetProblemDatas().items():
        print('CompressedSnapshots ', problemData.solutions[solutionName].GetCompressedSnapshots().get(0.0))


    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
