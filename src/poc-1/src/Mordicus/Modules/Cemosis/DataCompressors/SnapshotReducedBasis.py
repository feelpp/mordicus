# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

# from ast import MatMult
import os
# from statistics import correlation
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from mpi4py import MPI
from scipy import sparse
from petsc4py import PETSc
import petsc4py
from petsc4py import *
from slepc4py import SLEPc 


def ComputeReducedOrderBasisWithPOD(snapshotList, snapshotCorrelationOperator, tolerance=1.e-6):
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the
    snapshots contained in the iterator snapshotsIterator, which a correlation
    operator between the snapshots defined by the matrix
    snapshotCorrelationOperator, with tolerance as target accuracy of the data
    compression

    Parameters
    ----------
    snapshotList : List(of feelpp.functionSpace().element())
        List  of the snapshots on which we want to compute a reducedOrderBasis
    snapshotCorrelationOperator : feelpp.algMat
        correlation operator between the snapshots
    tolerance : float
        target accuracy of the data compression

    Returns
    -------
    np.ndarray
        of size (numberOfModes, numberOfDOFs)
    """

    snapshots = []

    numberOfDofs = snapshotList[0].functionSpace().nDof() 

    # snapshots = np.array(snapshots)

    # numberOfSnapshots = snapshots.shape[0]
    numberOfSnapshots = len(snapshotList)
    print('number of snapshots = ', numberOfSnapshots)
    
    #correlationMatrix = np.zeros((numberOfSnapshots, numberOfSnapshots))

    correlationMatrix = PETSc.Mat().create()
    correlationMatrix.setSizes([numberOfSnapshots, numberOfSnapshots])
    correlationMatrix.setFromOptions()
    correlationMatrix.setUp()

    for i, snapshot1 in enumerate(snapshotList):
        for j, snapshot2 in enumerate(snapshotList):
            if i >= j:
                correlationMatrix[i, j] = snapshotCorrelationOperator.energy(snapshot1, snapshot2)

    correlationMatrix.assemble()

    # Get eigenpairs of the correlation matrix 
    E = SLEPc.EPS() 
    E.create()  # create the solver 
    E.setOperators(correlationMatrix)
    E.setFromOptions()
    E.setWhichEigenpairs(E.Which.LARGEST_MAGNITUDE)
    E.setDimensions(numberOfSnapshots)

    E.solve()
    nbePODModes = E.getConverged() # number of eigenpairs 

    print("nbePODModes =", nbePODModes)

    eigenval = np.zeros(nbePODModes)

    eigenvect = PETSc.Vec().create()
    eigenvect.setSizes(nbePODModes)
    eigenvect.setFromOptions()
    eigenvect.setUp()

    eigenMatrix = PETSc.Mat().createDense(nbePODModes)
    # eigenMatrix.setSizes([nbePODModes, nbePODModes])
    eigenMatrix.setFromOptions()
    eigenMatrix.setUp()

    # eigenpairs = {}

    for i in range(nbePODModes):
        eigenval[i] = float(E.getEigenvalue(i).real)
        E.getEigenvector(i, eigenvect)
        # eigenpairs[eigenval[i]] = eigenvect/np.sqrt(eigenval[i]) # normalized eigenvect
        eigenMatrix[i,:] = eigenvect[:]/np.sqrt(eigenval[i])

    eigenMatrix.assemble()

    

    ## Set reduced basis 
    reducedOrderBasis = PETSc.Mat().createDense(size=(nbePODModes,numberOfDofs))
    reducedOrderBasis.setFromOptions()
    reducedOrderBasis.setUp()

    reducedOrderBasis.assemble()

    tempMat = reducedOrderBasis.copy()

    for i in range(nbePODModes):
        tempMat[i,:] = snapshotList[i].to_petsc().vec()[:]

    tempMat.assemble() 

    eigenMatrix.matMult(tempMat, reducedOrderBasis)

    return reducedOrderBasis



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)




