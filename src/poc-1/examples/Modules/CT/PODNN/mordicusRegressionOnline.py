from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.Containers import ProblemData as PD
#from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Modules.CT.OperatorCompressors import Regression
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Modules.CT.IO import MeshReader as MR
from Mordicus.Core.IO import StateIO as SIO
import numpy as np
from pathlib import Path
import os

def readSol(solutionName, nbeOfComponents, numberOfNodes, parameters, outputTimeSequence):   ###for the calculation of the regression error
   print('[INFO] Read Solutions for the calculation of the regression error...')
   from Mordicus.Modules.CT.IO import VTKSolutionReader as VSR
   collectionProblemDataEr = CPD.CollectionProblemData()

   for i in range(len(parameters)):
       print('parameter   ', parameters[i])
       folder = "Computation" + str(i) + "/"

       solutionEr = S.Solution(
           solutionName=solutionName,
           nbeOfComponents=nbeOfComponents,
           numberOfNodes=numberOfNodes,
           primality=True,
       )

       problemDataEr = PD.ProblemData(folder)
       problemDataEr.AddSolution(solutionEr)

       solutionReader = VSR.VTKSolutionReader(
               solutionEr.GetSolutionName()
       )

       count=0
       for t in outputTimeSequence:
           print('time   ', t)
           solutionFileName = folder + "cylinder_"

           snapshot = solutionReader.npRead(
               solutionFileName, int(t) 
           ) ###check this
           solutionEr.AddSnapshot(snapshot, t)
           problemDataEr.AddParameter(np.array(parameters[i]), t)
           count +=1

       collectionProblemDataEr.AddProblemData(problemDataEr)
       return collectionProblemDataEr


def test():

    initFolder = os.getcwd()
    currentFolder = str(Path(__file__).parents[0])
    os.chdir(currentFolder)

    ##################################################
    # LOAD DATA FOR ONLINE
    ##################################################
    VTKBase = MR.ReadVTKBase("meshBase.vtu")
    mesh = MR.ReadMesh("meshBase.vtu")
    #solutionName = "Mach"
    solutionName = "Pression"
    numberOfNodes = mesh.GetNumberOfNodes()
    nbeOfComponents = 1
    primality = True

    collectionProblemData = SIO.LoadState("mordicusState")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBasis = collectionProblemData.reducedOrderBases[solutionName]

    ##################################################
    # ONLINE
    ##################################################
    onlineCollectionProblemData = CPD.CollectionProblemData()  ###test

    parameters = np.array([[4.0]])   ###one parameter

    OnlineTimeSequence = np.array([0, 8])
    print("[INFO] OnlineTimeSequence...", OnlineTimeSequence)


    for i in range(len(parameters)):
      onlineFolder = "Online" + str(i) #test
      onlineProblemData = PD.ProblemData(onlineFolder) #test

      for t in OnlineTimeSequence:   ###note that the online parameters are given at the regression together
          onlineProblemData.AddParameter(parameters[i], t)
      print('[INFO] parameters for regression...\n', onlineProblemData.GetParameters())

      compressedSnapshots = Regression.ComputeOnline(
          onlineProblemData, operatorCompressionData, timep=True
      )

      solution = S.Solution(
          solutionName=solutionName,
          nbeOfComponents=nbeOfComponents,
          numberOfNodes=numberOfNodes,
          primality=primality,
      )
      onlineProblemData.AddSolution(solution)

      onlineProblemData.solutions[solutionName].SetCompressedSnapshots(compressedSnapshots)
      solution.UncompressSnapshots(reducedOrderBasis)

      onlineCollectionProblemData.AddProblemData(onlineProblemData)  ###test
    
    snapOn=[]
    for _, problemDOn in onlineCollectionProblemData.GetProblemDatas().items():
      for t in OnlineTimeSequence:
        snapOn.append(problemDOn.solutions[solutionName].GetSnapshot(t))

    #############################
    # Calculation of the regression error
    #############################
    collectionProblemDataEr = readSol(solutionName, nbeOfComponents, numberOfNodes, parameters, OnlineTimeSequence)
    
    snap=[]
    for _, problemDEr in collectionProblemDataEr.GetProblemDatas().items():
      for t in OnlineTimeSequence:
        snap.append(problemDEr.solutions[solutionName].GetSnapshot(t))

    epsNN=[]
    for i in range(len(snap)):
      epsNN.append(np.linalg.norm(snap[i] - snapOn[i]) / np.linalg.norm(snap[i]))

    epsNNM = sum(epsNN) / len(epsNN)

    print('[INFO] Results...')
    print('[INFO] snapOffline...', snap)
    print('[INFO] snapOnline...', snapOn)
    print('[INFO] epsNN...', epsNN)
    print('[INFO] epsNNM...', epsNNM)

    #############################


    ###write Rec. Solution
    from Mordicus.Modules.CT.IO import numpyToVTKWriter as NTV
    numpyToVTK = NTV.VTKWriter(VTKBase)
    numpyToVTK.numpyToVTKSanpWrite(solutionName, solution.GetSnapshotsList())

    os.chdir(initFolder)






    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
