from safran.IO import ZsetReader as ZR
from core.Containers import ProblemData as PD
from core.Containers.CompressedFormats import ModesAndCoefficients as MAC
from core.OperatorCompressors import Regression
import numpy as np



solutionName = "TP"
nbeOfComponents = 1
primality = True



##################################################
# LOAD DATA FOR ONLINE
##################################################

import pickle

operatorCompressionData = pickle.load(open('operatorCompressionData.pkl', 'rb'))
reducedOrderBasis = pickle.load(open('reducedOrderBasis.pkl', 'rb'))


##################################################
# ONLINE
##################################################

onlineProblemData = PD.ProblemData()

OnlineTimeSequence = np.array(np.arange(0,1001,50), dtype = float)

for t in OnlineTimeSequence:
    onlineProblemData.AddParameter(np.array([75., 2500.] + [t]), t)


compressedSnapshots = MAC.ModesAndCoefficients(solutionName, OnlineTimeSequence, nbeOfComponents, primality)


Regression.OnlineComputeRegression(onlineProblemData, operatorCompressionData, compressedSnapshots)
compressedSnapshots.SetModes(reducedOrderBasis)

compressedSnapshots.CheckDimensionsConsistence()



from genericROM.IO import PXDMFWriter as PW
mesh = ZR.ReadMesh("cube.geof")

PW.WritePXDMF(mesh, compressedSnapshots)
print("The compressed solution has been written in PXDMF Format")


