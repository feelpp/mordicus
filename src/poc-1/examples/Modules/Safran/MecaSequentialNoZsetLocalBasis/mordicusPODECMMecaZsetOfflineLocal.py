from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.Safran.FE import FETools as FT
from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP
from Mordicus.Modules.Safran.OperatorCompressors import Mechanical
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Core.Helpers import FolderHandler as FH
import numpy as np

def test():

    folderHandler = FH.FolderHandler(__file__)
    folderHandler.SwitchToScriptFolder()

    inputFileName = "cube.inp"
    meshFileName = "cube.geof"
    solutionFileName = "cube.ut"


    meshReader = ZMR.ZsetMeshReader("Computation1/"+meshFileName)

    print("Reading Mesh...")
    mesh = meshReader.ReadMesh()
    print("...done")

    print("ComputeL2ScalarProducMatrix...")
    snapshotCorrelationOperator = FT.ComputeL2ScalarProducMatrix(mesh, 3)
    SIO.SaveState("snapshotCorrelationOperator", snapshotCorrelationOperator)
    print("...done")

    numberOfNodes = mesh.GetNumberOfNodes()
    numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
    nbeOfComponentsPrimal = 3
    nbeOfComponentsDual = 6

    print("PreCompressOperator...")
    operatorPreCompressionData = Mechanical.PreCompressOperator(mesh)
    print("...done")

    collectionProblemDatas = []

    for i in range(2):

      collectionProblemData = CPD.CollectionProblemData()

      collectionProblemData.addVariabilityAxis('config',
                                             str,
                                             description="dummy variability")
      collectionProblemData.defineQuantity("U", "displacement", "m")
      collectionProblemData.defineQuantity("sig", "stress", "Pa")


      collectionProblemDatas.append(collectionProblemData)

      folders = ["Computation1/", "Computation2/"]

      for folder in folders:

        #inputReader = ZIR.ZsetInputReader(folder+inputFileName)
        solutionReader = ZSR.ZsetSolutionReader(folder+solutionFileName)

        solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
        solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)
        outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
        if i==0:
            outputTimeSequence = outputTimeSequence[:len(outputTimeSequence)//2+2]
        elif i==1:
            outputTimeSequence = outputTimeSequence[len(outputTimeSequence)//2-2:]


        #constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()

        problemData = PD.ProblemData(folder)
        problemData.AddSolution(solutionU)
        problemData.AddSolution(solutionSigma)
        #problemData.AddConstitutiveLaw(constitutiveLawsList)

        collectionProblemData.AddProblemData(problemData, config="case-"+str(i))

        for time in outputTimeSequence:
            U = solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True)
            solutionU.AddSnapshot(U, time)
            sigma = solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False)
            solutionSigma.AddSnapshot(sigma, time)

        SP.CompressData(collectionProblemData, "U", 1.e-4, snapshotCorrelationOperator)

        Mechanical.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-3)

        print("check compression...")
        reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U")
        collectionProblemData.CompressSolutions("U", snapshotCorrelationOperator)
        CompressedsolutionU = solutionU.GetCompressedSnapshots()
        compressionErrors = []
        for t in outputTimeSequence:
            reconstructedCompressedSolution = np.dot(CompressedsolutionU[t], reducedOrderBasis)
            exactSolution = solutionU.GetSnapshot(t)
            norml2ExactSolution = np.linalg.norm(exactSolution)
            if norml2ExactSolution != 0:
                relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExactSolution
            else:
                relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
            compressionErrors.append(relError)
        print("compressionErrors =", compressionErrors)


    for i in range(2):
        for j in [j for j in range(2) if j != i]:
            reducedOrderBasisJ = collectionProblemDatas[j].GetReducedOrderBasis("U")
            projectedReducedOrderBasis = collectionProblemDatas[i].ComputeReducedOrderBasisProjection("U", reducedOrderBasisJ, snapshotCorrelationOperator)
            collectionProblemDatas[i].SetDataCompressionData("projectedReducedOrderBasis_"+str(j), projectedReducedOrderBasis)

        SIO.SaveState("mordicusState_Basis_"+str(i), collectionProblemDatas[i])


    folderHandler.SwitchToExecutionFolder()

    assert np.max(compressionErrors) < 1.e-5, "!!! Regression detected !!! compressionErrors have become too large"


if __name__ == "__main__":
    test()
