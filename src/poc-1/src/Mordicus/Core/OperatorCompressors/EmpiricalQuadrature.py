import numpy as np
"""
Algorithms for empirical quadrature
"""

def computeMatrixAndVector(problemData, collectionProblemData, fieldHandler):
    """
    Arguments:
    ----------
    problemData : ProblemData
        new solution (1 parameter value, all time steps)
    reducedOrderBasisU : nparray(numberOfModes, numerOfDofs)
        reduced order basis
    fieldHandler : fieldHandlerBase
        field implementation to use for field manipulation (e.g. medcoupling...)
        
    Returns
    -------
    np.array, np.array : matrix and vector of empirical quadrature, allocated within routine
    """
    # k denotes the row of G
    return _addNewResultsToMatrixAndVector(problemData, collectionProblemData, fieldHandler, 0)


def _cdoubledot(fieldHandler, solutionUInstance, sigma, solutionSigmaInstance, u):
    """Computes SymGrad(u):sigma (doubly contracted product)
    """
    # Convert to MEDCouplingField
    fieldU = fieldHandler.ConvertToLocalField(solutionUInstance, u)
    fieldSigma = fieldHandler.ConvertToLocalField(solutionSigmaInstance, sigma)
    # Make the doubly contracted product
    fieldEpsilon = fieldHandler.symetricGradient(fieldU, solutionSigmaInstance)
    fieldDoublyContractedProduct = fieldHandler.doublyContractedProduct(fieldSigma, fieldEpsilon)
    return fieldDoublyContractedProduct

def _addNewResultsToMatrixAndVector(problemData, collectionProblemData, fieldHandler, k, G=None, Y=None):
    """
    Adds newly computed snapshots from problemData to the matrix and vector of empirical quadrature
    
    Arguments
    ---------
    problemData : ProblemData
        new solution (1 parameter value, all time steps)
    reducedOrderBasisU : nparray(numberOfModes, numerOfDofs)
        reduced order basis
    fieldHandler : fieldHandlerBase
        field implementation to use for field manipulation (e.g. medcoupling...)
    k : lines already in G and Y
    """
    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")

    # Initialisations pour la quadrature empirique
    numberOfModes, numerOfDofs = reducedOrderBasisU.shape
    solutionSigma = problemData.GetSolution("sigma")
    solutionUInstance = collectionProblemData.GetFieldInstance("U")
    numberOfRegisteredTimeSteps = len(solutionSigma.GetTimeSequenceFromSnapshots())
    if k == 0:
        G = np.zeros((numberOfRegisteredTimeSteps*numberOfModes, solutionSigma.GetNumberOfDofs()))
        Y = np.zeros((numberOfRegisteredTimeSteps*numberOfModes))

    for t in solutionSigma.GetTimeSequenceFromSnapshots():
        sigma = solutionSigma.GetSnapshot(t)
        solutionSigmaInstance = collectionProblemData.GetFieldInstance("sigma")
        
        for n in range(numberOfModes):
            u = reducedOrderBasisU[n,:]
            
            fieldDoublyContractedProduct = _cdoubledot(fieldHandler, solutionUInstance, sigma, solutionSigmaInstance, u)
            print("Converting from local field")
            
            # Convert back to numpy array
            G[k,:] = fieldHandler.ConvertFromLocalField(fieldDoublyContractedProduct)
            
            print("Integral")


            # The right-hand side is the integral of G[k,:]
            Y[k] = fieldHandler.integral(fieldDoublyContractedProduct, 0)
            k = k + 1

    return G, Y

def enrichMatrixAndVector(G, Y, problemData, collectionProblemData, fieldHandler, newmodes):
    """
    Enriches G and Y in-place with new rows

    Arguments:
    ----------
    G : np.array
       matrix of empirical quadrature offline stage
    Y : np.array
       right-hand side of empirical quadrature offline stage
    problemData : ProblemData
        new solution (1 parameter value, all time steps)
    reducedOrderBasisU : nparray(numberOfModes, numerOfDofs)
        reduced order basis
    fieldHandler : fieldHandlerBase
        field implementation to use for field manipulation (e.g. medcoupling...)
    """
    k = Y.size
    G, Y = _addNewResultsToMatrixAndVector(problemData, collectionProblemData, fieldHandler, k, G, Y)
    solutionUInstance = collectionProblemData.GetFieldInstance("U")
    k = Y.size
    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")

    for previousProblemData in collectionProblemData.GetProblemDatas():
        solutionSigma = previousProblemData.GetSolution("sigma")
        solutionSigmaInstance = collectionProblemData.GetFieldInstance("sigma")

        for t in solutionSigma.GetTimeSequenceFromSnapshots():
            sigma = solutionSigma.GetSnapshot(t)
            
            for n in range(newmodes):
                u = reducedOrderBasisU[n,:]
                fieldDoublyContractedProduct = _cdoubledot(fieldHandler, solutionUInstance, sigma, solutionSigmaInstance, u)
            
                # Convert back to numpy array
                G[k,:] = fieldHandler.ConvertFromLocalField(fieldDoublyContractedProduct)

                # The right-hand side is the integral of G[k,:]
                Y[k] = fieldHandler.integral(fieldDoublyContractedProduct, 0) 
                k = k + 1
    # TODO: yet to implement
    return G, Y

def solve(G, Y, volume, delta=1.e-5):
    """
    Solve for sparse empirical weignts
    """
    # Construction de la matrice A
    n = G.shape[0]
    m = G.shape[1]

    c = np.ones((m))
    null = np.zeros((n+1,m))
    tildeG = np.concatenate((G, np.ones((1,m))), axis = 0)
    #
    A = np.concatenate((tildeG, -tildeG), axis = 0)

    # Construction du second membre b
    tildey = np.concatenate((Y,[volume]), axis = 0)
    #
    #
    delta = 1.e-5
    d = delta * np.abs(tildey)
    #
    b = np.concatenate(((tildey + d), (-tildey+d)), axis=0)

    # For now, the linear programming problem is written in canonical form
    # Let us exand it to get a standard form
    #     and give it to the simplex implementation of scipy
    import scipy
    import scipy.optimize
    import numpy as np

    #res = scipy.optimize.linprog(c, method='simplex', A_ub=A, b_ub=b, bounds=(0, None))
    # For scipy >= 1, revised simplex allows to get rid of the tolerance
    res = scipy.optimize.linprog(c, method='revised simplex', A_ub=A, b_ub=b, bounds=(0, None), options={'tol': 1.e-9})
    return res.x