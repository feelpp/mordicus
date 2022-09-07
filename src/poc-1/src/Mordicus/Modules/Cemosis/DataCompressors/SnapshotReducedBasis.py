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

from Mordicus.Modules.Cemosis.Containers.SolutionStructure.FeelppSol import energy
from Mordicus.Core.DataCompressors import SnapshotPOD as SP


def orthogonality_check(Matrix,CorrelationMatrix):
    """
    This fucntion check for the pairwise orthogonality of the new basis
    """
    list_ = list(Matrix)
    dot_matrix = np.array([[np.dot(CorrelationMatrix.dot(item1), item2) for item1 in list_] for item2 in list_])
    if (dot_matrix - np.eye(dot_matrix.shape[0]) < 1e-10).all():
        return True
    else:
        error = dot_matrix - np.eye(dot_matrix.shape[0])
        print("max error with identity: ",np.max(error), "min error : ",np.min(error))
        return False

# ##### ALGO GREEDY ######
# # Number Of Modes can be a priori given or retrieve thanks to the tolerance threshold if no h1ScalarProducMatrix yields to L2 orthonormal basis

# def ComputeReducedOrderBasisWithGreedy(snapshotList, snapshotCorrelationOperator, NumberOfModes=0, tolerance=1.e-6):
#     """
#     Greedy algorithm for the construction of the reduced basis
#     orthogonal basis in H1 et L2 et orthonormalized in L2
#     #Algo as in https://hal.archives-ouvertes.fr/hal-01897395
#     """
#     # assert isinstance(solutionName, str)

#     # snapshotsIterator = collectionProblemData.SnapshotsIterator(solutionName)

#     # if snapshotCorrelationOperator is None:
#     #     snapshotCorrelationOperator = sparse.eye(collectionProblemData.GetSolutionsNumberOfDofs(solutionName))
    
#     snapshots = []

#     numberOfDofs = snapshotList[0].functionSpace().nDof() 

#     # snapshots = np.array(snapshots)

#     # numberOfSnapshots = snapshots.shape[0]
#     numberOfSnapshots = len(snapshotList)
#     print('number of snapshots = ', numberOfSnapshots)


#     snapshots = []
#     SnaphotsNorm=[]
#     for snap in snapshotList:
#         snapshots.append(snap.to_petsc().vec()[:])
#         SnaphotsNorm.append(snapshotCorrelationOperator.energy(snap, snap))
    
#     snapshots = np.array(snapshots)
    
#     # DegreesOfFreedom=np.shape(snapshotCorrelationOperator)[0]
#     # NumberOfSnapshots=np.shape(snapshots)[0]

#     # if CheckLinearIndependence(snapshots) != True: ##If dependence, remove the vectors
#     #     print("snapshots linearly dependent, removing the corresponding vectors")
#     #     Inds=Check
#     #     snapshots=snapshots[Inds]
#     #     SnaphotsNorm=SnaphotsNorm[Inds]
#     #     NumberOfSnapshots=len(Inds)

#     if NumberOfModes==0:
        
#         reducedOrderBasis = PETSc.Mat().createDense(size=(numberOfSnapshots,numberOfDofs))
#     else:
#         reducedOrderBasis= PETSc.Mat().createDense(size=(NumberOfModes,numberOfDofs))
    
#     reducedOrderBasis.setFromOptions()
#     reducedOrderBasis.setUp()
#     reducedOrderBasis.assemble()
    

#     Index=SnaphotsNorm.index(max(SnaphotsNorm)) #first mode
#     print("Mode 0: ", Index)
#     reducedOrderBasis[0,:]=snapshotList[Index].to_petsc().vec()[:]/SnaphotsNorm[Index] #first mode
#     ListeIndex=[Index] #first snapshot 
#     BasisNorm=[SnaphotsNorm[Index]]
#     Basis=[snapshots[Index]]

#     MatrixBasisProduct=[snapshotCorrelationOperator.dot(Basis[0])]

#     if NumberOfModes>0:
#         for n in range(1,NumberOfModes):
#             print("Mode: ",n)
        
#             TestVector=dict() # dictionnary: vector in the reduced basis if maxTest if maximum
#             for j in range(numberOfSnapshots): 
#                 if not (j in ListeIndex) and SnaphotsNorm[j]>1e-10: #if index not yet in the basis
#                     for s in range(len(Basis)):
#                         projectU += Basis[s]. 
#                     w=snapshots[j]- np.sum((b*np.dot(MatrixBasisProduct[k],snapshots[j])/BasisNorm[k]**2 for k,b in enumerate(Basis)),axis=0)#potential vector to add in the reduced basis

#                     if (w > 1e-10).any():
#                         NormW=Norm(snapshotCorrelationOperator,w)#np.sqrt(np.dot((l2ScalarProducMatrix.dot(w)),w))
#                         GreedyMaximumTest=NormW/SnaphotsNorm[j] #we seek the max
#                         TestVector[j]=[GreedyMaximumTest,w,NormW]
  
#             Index=max(TestVector, key = lambda k: TestVector[k][0]) #index of the snapshot used
#             print("index",Index)
#             ListeIndex.append(Index) #adding in the list
        
#             Basis.append(TestVector[Index][1])
#             BasisNorm.append(TestVector[Index][2])
#             MatrixBasisProduct.append(snapshotCorrelationOperator.dot(Basis[n]))
                                
#             reducedOrderBasisU[n,:]=(TestVector[Index][1]/TestVector[Index][2]) #orthonormalization in L2

#     else:
#         Threshold,n=1e18,0 #init
#         while Threshold>Tol: #iteratation
#             n+=1
#             print("Mode: ",n)
        
#             TestVector=dict() # dictionnary: vector in the reduced basis if maxTest if maximum
#             for j in range(NumberOfSnapshots): 
#                 if not (j in ListeIndex) and SnaphotsNorm[j]>1e-10: #if index not yet in the basis
#                     w=snapshots[j]-np.sum((np.dot(MatrixBasisProduct[k],snapshots[j])/(BasisNorm[k]**2)*b for k,b in enumerate(Basis)),axis=0)#potential vector to add in the reduced basis
#                     if (w > 1e-10).any():
#                         NormW=Norm(snapshotCorrelationOperator,w)#np.sqrt(np.dot((l2ScalarProducMatrix.dot(w)),w))
#                         GreedyMaximumTest=NormW/SnaphotsNorm[j] #we seek the max
#                         TestVector[j]=[GreedyMaximumTest,w,NormW]
  
#             Index=max(TestVector, key = lambda k: TestVector[k][0]) #index of the snapshot used
#             # print(TestVector[Index])
#             print("index",Index)
#             ListeIndex.append(Index) #adding in the list
#             assert TestVector[Index][0]<Threshold, f"error: Tolerance too big {TestVector[Index][0]} vs {Threshold}"
#             Threshold=TestVector[Index][0]
#             Basis.append(TestVector[Index][1])
#             BasisNorm.append(TestVector[Index][2])
#             MatrixBasisProduct.append(snapshotCorrelationOperator.dot(Basis[n]))
                                
#             reducedOrderBasisU[n,:]=(TestVector[Index][1]/TestVector[Index][2]) #orthonormalization in L2
#             NumberOfModes=n+1
#             print("NumberOfModes", NumberOfModes)
#         reducedOrderBasisU=reducedOrderBasisU[0:NumberOfModes,:] #keep the first numberOfModes basis vectors
    
        
#     Check=orthogonality_check(reducedOrderBasisU,snapshotCorrelationOperator)
#     print("orthogonality ", Check) #if no orthogonality, it may be due to linear dependence of vectors/ non-stability of GS
#     if Check==False: #redo Gram-Schmidt procedure 
#         NewReducedOrderBasisU=np.zeros((NumberOfModes,DegreesOfFreedom))
#         BasisNorm=[Norm(snapshotCorrelationOperator,reducedOrderBasisU[0])]
#         NewReducedOrderBasisU[0]=reducedOrderBasisU[0]/BasisNorm[0]
        
#         for i in range(1,NumberOfModes):
#             NewReducedOrderBasisU[i]=reducedOrderBasisU[i]-np.sum((NewReducedOrderBasisU[k]*np.dot(snapshotCorrelationOperator.dot(NewReducedOrderBasisU[k]),reducedOrderBasisU[i])/(BasisNorm[k]**2) for k in range(i)),axis=0)#potential vector to add in the reduced basis
#             BasisNorm.append(Norm(snapshotCorrelationOperator,NewReducedOrderBasisU[i]))
#         for i in range(NumberOfModes):
#             reducedOrderBasisU[i]=NewReducedOrderBasisU[i]/BasisNorm[i]#Norm(snapshotCorrelationOperator,NewReducedOrderBasisU[i])
#     Check=orthogonality_check(reducedOrderBasisU,snapshotCorrelationOperator)
#     print("orthogonality ", Check) #if no orthogonality, it may be due to linear dependence of vectors/ non-stability of GS

#     """
#     for i in range(NumberOfModes):
#         for j in range(i+1):
#             t=snapshotCorrelationOperator.dot(reducedOrderBasisU[i,:])
#             norm=t.dot(reducedOrderBasisU[j,:])
#             print(i,j," ",norm)
#     """
#     ### H1 Orthogonalization
      
#     if h1ScalarProducMatrix!=None:
#         normRed=[]
#         K=np.zeros((NumberOfModes,NumberOfModes)) #rigidity matrix
#         M=np.zeros((NumberOfModes,NumberOfModes)) #mass matrix
#         for i in range(NumberOfModes):
#             matVecH1=h1ScalarProducMatrix.dot(reducedOrderBasisU[i,:])
#             matVecL2=snapshotCorrelationOperator.dot(reducedOrderBasisU[i,:])
#             for j in range(NumberOfModes):
#                 if i>=j:
                   
#                     K[i,j]=np.dot(matVecH1,reducedOrderBasisU[j,:])
#                     M[i,j]=np.dot(matVecL2,reducedOrderBasisU[j,:])
#                     K[j,i]=K[i,j]
#                     M[j,i]=M[i,j]
    
    
#         # on resoud Kv=lambd Mv
#         #mpiReducedCorrelationMatrixM = np.zeros((nev, nev))
#         #MPI.COMM_WORLD.Allreduce([M,  MPI.DOUBLE], [mpiReducedCorrelationMatrixM,  MPI.DOUBLE])
#         eigenValues,vr=linalg.eig(K, b=M) #eigenvalues + right eigenvectors
#         idx = eigenValues.argsort()[::-1]
#         eigenValues = eigenValues[idx]
#         eigenVectors = vr[:, idx]
#         reducedOrderBasisU=np.dot(eigenVectors.transpose(),reducedOrderBasisU)

#         for i in range(NumberOfModes):
#             reducedOrderBasisNorm=np.sqrt(reducedOrderBasisU[i,:]@(snapshotCorrelationOperator@reducedOrderBasisU[i,:]))
#             reducedOrderBasisU[i,:]/=reducedOrderBasisNorm#np.sqrt(M[i,i]) #L2 orthonormalization
    
#     return reducedOrderBasisU



def PODReducedBasisNumpy(snapshotList, snapshotCorrelationOperator, tolerance=1.e-6):
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the
    snapshots contained in the list snapshotList, which a correlation
    operator between the snapshots defined by the matrix
    snapshotCorrelationOperator, with tolerance as target accuracy of the data
    compression

    This function convert PETSc matrix and vector to numpy and use numpy computation 
    (not so efficient)
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


    oper = snapshotCorrelationOperator.mat()
    oper.assemble()
    oper = np.array(oper[:,:])
    snaparray = []
    for s in snapshotList:
        snaparray.append(s.to_petsc().vec()[:])

    rbb = SP.ComputeReducedOrderBasis(snaparray, oper, tolerance)

    nbPODMode = rbb.shape[0]
    nbDofs = snapshotList[0].functionSpace().nDof() 
    reducedOrderBasisU = PETSc.Mat().createDense(size=(nbPODMode,nbDofs))
    reducedOrderBasisU.setFromOptions()
    reducedOrderBasisU.setUp()
    reducedOrderBasisU.assemble()
    reducedOrderBasisU[:,:] = rbb

    return reducedOrderBasisU


def PODReducedBasisPETSc(snapshotList, snapshotCorrelationOperator, tolerance=1.e-6):
    """
    Computes a reducedOrderBasis using the SnapshotPOD algorithm, from the
    snapshots contained in the list snapshotList, which a correlation
    operator between the snapshots defined by the matrix
    snapshotCorrelationOperator, with tolerance as target accuracy of the data
    compression

    All the computation are done in PETSc environnement 
    
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

    numberOfSnapshots = len(snapshotList)
    print('number of snapshots = ', numberOfSnapshots)

    correlationMatrix = PETSc.Mat().create()
    correlationMatrix.setSizes([numberOfSnapshots, numberOfSnapshots])
    correlationMatrix.setFromOptions()
    correlationMatrix.setUp()

    for i, snapshot1 in enumerate(snapshotList):
        for j, snapshot2 in enumerate(snapshotList):
                correlationMatrix[i, j] = snapshotCorrelationOperator.energy(snapshot1, snapshot2)

    correlationMatrix.assemble()

    eigenValues, eigenVectors =  TruncatedEVDPetscMat(correlationMatrix, tolerance) # truncate only eigenvalu >0 

    nbePODModes = len(eigenVectors)

    print("nbePODModes =", nbePODModes)

    eigenMatrix = PETSc.Mat().createDense([nbePODModes,numberOfSnapshots])
    eigenMatrix.setFromOptions()
    eigenMatrix.setUp()


    for i in range(nbePODModes):
        eigenMatrix[i,:] = eigenVectors[i]/np.sqrt(eigenValues[i])

    eigenMatrix.assemble()
    

    ## Set reduced basis 
    tempMat = PETSc.Mat().createDense(size=(numberOfSnapshots,numberOfDofs))
    tempMat.setFromOptions()
    tempMat.setUp()
    tempMat.assemble()

    for i in range(numberOfSnapshots):
        tempMat[i,:] = snapshotList[i].to_petsc().vec()[:]

    tempMat.assemble() 


    reducedOrderBasis = PETSc.Mat().createDense(size=(nbePODModes,numberOfDofs))
    reducedOrderBasis.setFromOptions()
    reducedOrderBasis.setUp()
    reducedOrderBasis.assemble()

    eigenMatrix.matMult(tempMat, reducedOrderBasis)

    # oper = snapshotCorrelationOperator.mat()
    # oper.assemble()
    # # reducedOrderBasis.assemble()

    # oper = np.array(oper[:,:]) 
    # rb = reducedOrderBasis[:,:]


    # for i in range(nbePODModes):
    #     # reducedOrderBasisNorm= np.sqrt(snapshotCorrelationOperator.energy(reducedOrderBasis[i,:], reducedOrderBasis[i,:]))
    #     reducedOrderBasisNorm= np.sqrt(energy(oper[:,:], rb[i,:]))
    #     rb[i,:]/=reducedOrderBasisNorm # L2 orthonormalization

    # reducedOrderBasis[:,:] = rb

    # check = orthogonality_check(rb,oper)
    # print("orthogonality = ", check )
    return reducedOrderBasis


def TruncatedEVDPetscMat(matrix, epsilon = None, nbModes = None):
    """
    Computes a truncated eigen value decomposition of a symetric definite
    matrix in petsc.mat format. Get only eigen value lambda_i > epsilon^2 lambda_max
    the basis vectors returned are orthonormalized 

    Parameters
    ----------
    matrix : petsc.Mat 
        the input matrix
    epsilon : float
        the truncation tolerence, determining the number of keps eigenvalues
    nbModes : int
        the number of keps eigenvalues

    Returns
    -------
    np.ndarray
        kept eigenvalues, of size (numberOfEigenvalues)
    np.ndarray
        kept eigenvectors, of size (numberOfEigenvalues, numberOfSnapshots)
    """

    if epsilon != None and nbModes != None:# pragma: no cover
        raise("cannot specify both epsilon and nbModes")

    # Get eigenpairs of the matrix 
    E = SLEPc.EPS() # SVD for singular value decomposition or EPS for Eigen Problem Solver  
    E.create()  # create the solver

    E.setOperators(matrix)
    E.setFromOptions()
    E.setWhichEigenpairs(E.Which.LARGEST_MAGNITUDE)
    E.setDimensions(matrix.size[1]) # set the number of eigen val to compute
    # E.setTolerances(epsilon) # set the tolerance used for the convergence 

    E.solve()
    nbmaxEv = E.getConverged() # number of eigenpairs 

    # print('Does it converge ? (1 or 0) =', E.getConvergenceTest())
    # print('Is it positive mat ? (1 or 0)', E.isPositive() )
 

    eigenValues = []
    eigenVectors = E.getInvariantSubspace() # Get orthonormal basis associated to eigenvalues 

    # eigenvect = PETSc.Vec().create()
    # eigenvect.setSizes(nbmaxEv)
    # eigenvect.setFromOptions()
    # eigenvect.setUp()

    for i in range(nbmaxEv):
        eigenValues.append(float(E.getEigenvalue(i).real))
        # E.getEigenvector(i, eigenvect)
        # eigenVectors.append(eigenvect)
    
    E.destroy() # destroy the solver object 

    eigenValues = np.array(eigenValues)

    idx = eigenValues.argsort()[::-1]

    eigenValues = eigenValues[idx]
    eigenVectors = [eigenVectors[i] for i in idx]

    if nbModes == None:
        if epsilon == None:
            nbModes  = matrix.size[0]
        else:
            nbModes = 0
            bound = (epsilon ** 2) * eigenValues[0]
            for e in eigenValues:
                if e > bound:
                    nbModes += 1
            id_max2 = 0
            bound = (1 - epsilon ** 2) * np.sum(eigenValues)
            temp = 0
            for e in eigenValues:
                temp += e
                if temp < bound:
                    id_max2 += 1  # pragma: no cover

            nbModes = max(nbModes, id_max2)

    if nbModes > matrix.size[0]:
        print("nbModes taken to max possible value of "+str(matrix.shape[0])+" instead of provided value "+str(nbModes))
        nbModes = matrix.size[0]

    index = np.where(eigenValues<0)
    if len(eigenValues[index])>0:
        if index[0][0]<nbModes:
            #print(nbModes, index[0][0])
            print("removing numerical noise from eigenvalues, nbModes is set to "+str(index[0][0])+" instead of "+str(nbModes))
            nbModes = index[0][0]
    
    return eigenValues[0:nbModes], eigenVectors[0:nbModes]




if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)




