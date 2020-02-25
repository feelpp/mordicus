from Mordicus.Modules.Scilab_ESI_Group.SciMeshReader import SciMeshReader as SciMR
from Mordicus.Core.Containers.ProblemData import ProblemData 
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

    print('Create mesh')
    reader2 = SciMR(currentFolder)
    mesh = reader2.ReadMesh()
    print(mesh)

    numberOfNodes = mesh.GetNumberOfNodes()
    primality = True

    dataFolder = '.'
    problemData = ProblemData(dataFolder)

    parameters = [[0.3, 0.0], [0.3, 5.0], [0.3, 10.0], [0.3, 15.0]]

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


        count=0
        for t in outputTimeSequence:
            print('\ntime   ', t)
            #solutionFileName = folder + "fields_"+str(count)+".vtu"
            solutionFileName = folder + "fields_"+str(count)+".npy"
            solutionReader = VSR.VTKSolutionReader(solutionFileName)

            snapshot = solutionReader.npReadSnapshot(
                solution.GetSolutionName(), t, nbeOfComponents
            )
            solution.AddSnapshot(snapshot, t)
            problemData.AddParameter(np.array(parameters[i]), t)
            print('Data      ' , solutionFileName)
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
