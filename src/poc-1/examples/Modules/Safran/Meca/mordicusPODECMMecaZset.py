from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Core.DataCompressors import SnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanics as Meca
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
import numpy as np
from pathlib import Path
import os


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)




    folder = "Computation1/"

    inputFileName = folder + "cube.inp"
    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"

    meshReader = ZMR.ZsetMeshReader(meshFileName)
    inputReader = ZIR.ZsetInputReader(inputFileName)
    solutionReader = ZSR.ZsetSolutionReader(solutionFileName)


    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")



    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    nbeOfComponentsPrimal = mesh.GetDimensionality()
    nbeOfComponentsDual = 6

        
    outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
        

    solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, True)
    solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, False)


        
    for t in outputTimeSequence:
            
            U1 = solutionReader.ReadSnapshot("U1", t, primality=True)
            U2 = solutionReader.ReadSnapshot("U2", t, primality=True)
            U3 = solutionReader.ReadSnapshot("U3", t, primality=True)
            solutionU.AddSnapshot(t, np.concatenate([U1, U2, U3]))
            
            sig11 = solutionReader.ReadSnapshot("sig11", t, primality=False)
            sig22 = solutionReader.ReadSnapshot("sig22", t, primality=False)
            sig33 = solutionReader.ReadSnapshot("sig33", t, primality=False)
            sig12 = solutionReader.ReadSnapshot("sig12", t, primality=False)
            sig23 = solutionReader.ReadSnapshot("sig23", t, primality=False)
            sig31 = solutionReader.ReadSnapshot("sig31", t, primality=False)
            solutionSigma.AddSnapshot(t, np.concatenate([sig11, sig22, sig33, sig12, sig23, sig31]))


    problemData = PD.ProblemData("myComputation")
    problemData.AddSolution(solutionU)
    problemData.AddSolution(solutionSigma)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.AddProblemData(problemData)
        
    print("ComputeL2ScalarProducMatrix...")
    l2ScalarProducMatrix = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    collectionProblemData.SetSnapshotCorrelationOperator("U", l2ScalarProducMatrix)
        
    reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(
            collectionProblemData, "U", 1.e-5
    )
    collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
    SP.CompressSolutionsOfCollectionProblemData(collectionProblemData, "U")


    CompressedSolutionU = solutionU.GetCompressedSnapshots()

    compressionErrors = []

    for t in outputTimeSequence:
        reconstructedCompressedSolution = np.dot(CompressedSolutionU[t], reducedOrderBasisU)
        exactSolution = solutionU.GetSnapshot(t)
        norml2ExactSolution = np.linalg.norm(exactSolution)
        if norml2ExactSolution != 0:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
        else:
            relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
        compressionErrors.append(relError)

    print("compressionErrors =", compressionErrors)



    PW.WritePXDMFFromSolution(mesh, solutionU, reducedOrderBasisU)

    operatorCompressionData = Meca.CompressMecaOperator(
            collectionProblemData, mesh, 1.e-5
    )
    

    os.chdir(initFolder)    

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
