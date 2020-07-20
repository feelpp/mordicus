import numpy as np
"""
Algorithms for empirical quadrature
"""

def computeMatrixAndVector(problemData, reducedOrderBasisU, fieldHandler):
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
    return _addNewResultsToMatrixAndVector(problemData, reducedOrderBasisU, fieldHandler, 0)


def _cdoubledot(fieldHandler, solutionUStructure, sigma, solutionSigmaStructure, u):
    """Computes u:sigma
    """
    # Convert to MEDCouplingField
    fieldU = fieldHandler.ConvertToLocalField(solutionUStructure, u)
    fieldSigma = fieldHandler.ConvertToLocalField(solutionSigmaStructure, sigma)
# Make the doubly contracted product
    fieldEpsilon = fieldHandler.symetricGradient(fieldU)
    fieldDoublyContractedProduct = fieldHandler.doublyContractedProduct(fieldSigma, fieldEpsilon)
    return fieldDoublyContractedProduct

def _addNewResultsToMatrixAndVector(problemData, reducedOrderBasisU, fieldHandler, k, G=None, Y=None):
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
    # Initialisations pour la quadrature empirique
    numberOfModes, numerOfDofs = reducedOrderBasisU.shape
    solutionSigma = problemData.GetSolution("sigma")
    solutionUStructure = problemData.GetSolution("U").GetStructure()
    numberOfRegisteredTimeSteps = len(solutionSigma.GetTimeSequenceFromSnapshots())
    if k == 0:
        G = np.zeros((numberOfRegisteredTimeSteps*numberOfModes, solutionSigma.GetNumberOfDofs()))
        Y = np.zeros((numberOfRegisteredTimeSteps*numberOfModes))

    for t in solutionSigma.GetTimeSequenceFromSnapshots():
        sigma = solutionSigma.GetSnapshot(t)
        solutionSigmaStructure = solutionSigma.GetStructure()
        
        for n in range(numberOfModes):
            u = reducedOrderBasisU[n,:]
            
            fieldDoublyContractedProduct = _cdoubledot(fieldHandler, solutionUStructure, sigma, solutionSigmaStructure, u)
            
            # Convert back to numpy array
            G[k,:] = fieldHandler.ConvertFromLocalField(fieldDoublyContractedProduct)

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
    reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")
    G, Y = _addNewResultsToMatrixAndVector(problemData, reducedOrderBasisU, fieldHandler, k, G, Y)
    solutionUStructure = problemData.GetSolution("U").GetStructure()
    k = Y.size
    for previousProblemData in collectionProblemData.GetProblemDatas():
        solutionSigma = previousProblemData.GetSolution("sigma")
        solutionSigmaStructure = solutionSigma.GetStructure()

        for t in solutionSigma.GetTimeSequenceFromSnapshots():
            sigma = solutionSigma.GetSnapshot(t)
            
            for n in range(newmodes):
                u = reducedOrderBasisU[n,:]
                fieldDoublyContractedProduct = _cdoubledot(fieldHandler, solutionUStructure, sigma, solutionSigmaStructure, u)
            
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