from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Core.Containers import CollectionProblemData as CPD
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

    collectionProblemData = CPD.Load("mordicusState.pkl")
    operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
    reducedOrderBasis = collectionProblemData.reducedOrderBases["TP"]


    ##################################################
    # ONLINE
    ##################################################

    onlineProblemData = PD.ProblemData("Online")

    OnlineTimeSequence = np.array(np.arange(0, 1001, 50), dtype=float)

    for t in OnlineTimeSequence:
        onlineProblemData.AddParameter(np.array([75.0, 2500.0] + [t]), t)


    compressedSnapshots = Regression.ComputeApproximation(
        onlineProblemData, operatorCompressionData
    )


    mesh = ZMR.ReadMesh("cube.geof")

    PW.WritePXDMF(mesh, compressedSnapshots, reducedOrderBasis, "TP")
    print("The compressed solution has been written in PXDMF Format")
    


    os.chdir(initFolder)    

    return "ok"

if __name__ == "__main__":
    print(test())  # pragma: no cover
