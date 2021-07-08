# -*- coding: utf-8 -*-
## NIRB script python Greedy Algorithm

## Elise Grosjean
## 01/2021


from BasicTools.FE import FETools as FT
import numpy as np
from scipy import linalg

##### ALGO GREEDY ######
def Greedy(collectionProblemData,solutionName,snapshotCorrelationOperator,h1ScalarProducMatrix,nev):
    """
    Greedy algorithm for the construction of the reduced basis
    orthogonal basis in H1 et L2 et orthonormalized in L2
    #Algo as in https://hal.archives-ouvertes.fr/hal-01897395
    """
    assert isinstance(solutionName, str)

    snapshotsIterator = collectionProblemData.SnapshotsIterator(solutionName)

    if snapshotCorrelationOperator is None:
        snapshotCorrelationOperator = sparse.eye(collectionProblemData.GetSolutionsNumberOfDofs(solutionName))
    l2ScalarProducMatrix=snapshotCorrelationOperator
    snapshots = []
    
    for s in snapshotsIterator:
        snapshots.append(s)

    snapshots = np.array(snapshots)
    
    nbdegree=np.shape(l2ScalarProducMatrix)[0]
    ns=np.shape(snapshots)[0]
    #print(nbdegree)
    reducedOrderBasisU=np.zeros((nev,nbdegree)) #nev, nbd

    norm0=np.sqrt(snapshots[0]@l2ScalarProducMatrix@snapshots[0]) #norm L2 u0
    reducedOrderBasisU[0,:]=snapshots[0]/norm0 #first mode
    ListeIndex=[0] #first snapshot 

    basis=[]
    basis.append(np.array(snapshots[0]))
    
    for n in range(1,nev):
        #print("nev ",n)
        vecteurTest=dict() # dictionnary: vector in the reduced basis if maxTest if maximum
        for j in range(ns): 
            if not (j in ListeIndex): #if index not yet in the basis
                
                coef=[snapshots[j]@(l2ScalarProducMatrix@b) for b in basis]
                w=snapshots[j]-sum((snapshots[j]@(l2ScalarProducMatrix@b))/(b@l2ScalarProducMatrix@b)*b for b in basis)#potential vector to add in the reduced basis
                norml2=np.sqrt(w@(l2ScalarProducMatrix@w))
                normj=np.sqrt(snapshots[j]@l2ScalarProducMatrix@snapshots[j]) #norm L2 uj
                maxTest=norml2/normj #we seek the max
                vecteurTest[j]=[maxTest,w]
               
        ind=max(vecteurTest, key = lambda k: vecteurTest[k][0]) #index of the snapshot used
        #print("index",ind)
        ListeIndex.append(ind) #adding in the list
        norm=np.sqrt(vecteurTest[ind][1]@(l2ScalarProducMatrix@vecteurTest[ind][1]))
        basis.append(vecteurTest[ind][1])
        reducedOrderBasisU[n,:]=(vecteurTest[ind][1]/norm) #orthonormalization in L2

    ### H1 Orthogonalization
    K=np.zeros((nev,nev)) #rigidity matrix
    M=np.zeros((nev,nev)) #mass matrix
    for i in range(nev):
        for j in range(nev):
            K[i,j]=reducedOrderBasisU[i,:]@h1ScalarProducMatrix@reducedOrderBasisU[j,:]
            M[i,j]=reducedOrderBasisU[i,:]@l2ScalarProducMatrix@reducedOrderBasisU[j,:]
    eigenValues,vr=linalg.eig(K, b=M) #eigenvalues + right eigenvectors
    idx = eigenValues.argsort()[::-1]
    eigenValues = eigenValues[idx]
    eigenVectors = vr[:, idx]
    reducedOrderBasisU=np.dot(eigenVectors.transpose(),reducedOrderBasisU)

    for i in range(nev):
        reducedOrderBasisNorm=np.sqrt(reducedOrderBasisU[i,:]@(l2ScalarProducMatrix@reducedOrderBasisU[i,:]))
        reducedOrderBasisU[i,:]/=reducedOrderBasisNorm #L2 orthonormalization
    return reducedOrderBasisU



## Rectification Post-Process
def Rectification(collectionProblemData,FineSolutionName,CoarseSolutionName,snapshotCorrelationOperator,nev):
    print("caution: for rectification, the snapshots must be read in the same order")
    assert isinstance(FineSolutionName, str)
    assert isinstance(CoarseSolutionName, str)
    snapshotsIterator = collectionProblemData.SnapshotsIterator(FineSolutionName)

    if snapshotCorrelationOperator is None:
        snapshotCorrelationOperator = sparse.eye(collectionProblemData.GetSolutionsNumberOfDofs(solutionName))

    snapshots = [] #fine snapshots
    snapshotsH = [] #coarse snapshots
    for s in snapshotsIterator:
        snapshots.append(s)

    snapshots = np.array(snapshots)

    ns=np.shape(snapshots)[0]
    snapshotsHIterator = collectionProblemData.SnapshotsIterator(CoarseSolutionName)
    for s in snapshotsHIterator:
        snapshotsH.append(s)

    snapshotsH = np.array(snapshotsH)
    
    alpha=np.zeros((ns,nev))
    beta=np.zeros((ns,nev))

    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis(FineSolutionName)
    for i in range(ns):
        for j in range(nev):
            alpha[i,j]=snapshots[i]@(snapshotCorrelationOperator@reducedOrderBasisU[j,:])
            beta[i,j]=snapshotsH[i]@(snapshotCorrelationOperator@reducedOrderBasisU[j,:])

    lambd=1e-10 #regularization (AT@A +lambda I_d)^-1
    R=np.zeros((nev,nev))
    for i in range(nev):
        R[i,:]=(np.linalg.inv(beta.transpose()@beta+lambd*np.eye(nev))@beta.transpose()@alpha[:,i])
    #print("Rectification matrix: ",R)
    return R

def addRectificationTocollectionProblemData(collectionProblemData,FineSolutionName,CoarseSolutionName,snapshotCorrelationOperator,nev):
    R=Rectification(collectionProblemData,FineSolutionName,CoarseSolutionName,snapshotCorrelationOperator,nev)
    collectionProblemData.SetDataCompressionData("Rectification",R)
