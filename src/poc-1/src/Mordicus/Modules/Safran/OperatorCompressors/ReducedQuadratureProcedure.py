# -*- coding: utf-8 -*-

import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np
import sys

from BasicTools.Helpers.TextFormatHelper import TFormat
from Mordicus.Modules.Safran.BasicAlgorithms import NNOMPA
from Mordicus.Modules.Safran.BasicAlgorithms import LPEQP



def ComputeReducedIntegrationScheme(integrationWeights, integrands, tolerance,\
        imposedIndices = None, reducedIntegrationPointsInitSet = None,\
        initByLPEQP = False, nRandom = 1, geoMorphingMultiplier = None):
    """
    Parameters
    ----------
    integrationWeights : np.ndarray
        of size (numberOfIntegrationPoints,), dtype = float.
        Weights of the truth quadrature

    integrands : np.ndarray
        of size (numberOfIntegrands,numberOfIntegrationPoints), dtype = float.
        Functions we look to integrated accurately with fewer integration
        points. Usually, the integrands are already reduced, and
        numberOfIntegrands is the product of the number of reduced integrand
        modes and the number of modes of the ReducedOrderBasis

    tolerance : float
        upper bound for the accuracy of the reduced integration scheme on the
        provided integrands

    imposedIndices : np.ndarray
        of size (numberOfImposedIndices,), dtype = int.
        Optional.
        Indicies required to be selected in the reduced integration scheme

    reducedIntegrationPointsInitSet : np.ndarray
        of size (numberOfInitReducedIntegratonPoints,), dtype = int.
        Optional.
        Initial guess for the indices of the reducedIntegrationScheme.

    initByLPEQP : bool
        Optional.
        Runs a preliminary LPEQP stage if True


    Returns
    -------
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = int
        s: indices of the kepts integration points (reducedIntegrationPoints)
    np.ndarray of size (numberOfReducedIntegrationPoints,), dtype = float
        x: weights associated to the kepts integration points
        (reducedIntegrationWeights)
    """

    if imposedIndices is None:
        imposedIndices = []

    if reducedIntegrationPointsInitSet is None:
        reducedIntegrationPointsInitSet = []

    """if geoMorphingMultiplier is not None:
        for i in range(integrands.shape[0]):
            integrands[i] = np.multiply(geoMorphingMultiplier, integrands[i])"""


    print(TFormat.InGreen("Starting computing reduced integration scheme "\
    "for "+str(integrands.shape[0])+" integrands having "\
    +str(integrands.shape[1])+" integration points"))

    # add the unity integrand for volume computation
    numberOfIntegrationPoints = integrands.shape[1]
    #integrands = np.vstack((integrands, np.ones(numberOfIntegrationPoints)))

    # compute the integrations using the exact quadrature
    integrals = np.dot(integrands, integrationWeights)


    normIntegrals = np.linalg.norm(integrals)


    if initByLPEQP == True:

        # LPEQP stage
        print(TFormat.InGreen("LPEQP stage"))
        s, x = LPEQP.LPEQP(integrationWeights,integrands,integrals,\
                           normIntegrals,tolerance)
        PrintReducedSchemeStatistics(s, x, integrands, integrals, normIntegrals)

    else:
        if len(reducedIntegrationPointsInitSet) == 0:
            s = np.empty(0, dtype = int)
        else:
            s = reducedIntegrationPointsInitSet


    # NNOMPA stage
    print(TFormat.InGreen("NNOMPA stage"))

    s, x = NNOMPA.NNOMPA(integrationWeights,integrands,integrals,normIntegrals,\
                       tolerance, s, nRandom = nRandom)
    PrintReducedSchemeStatistics(s, x, integrands, integrals, normIntegrals)



    # add imposed indices
    l1 = s.shape[0]
    s = np.array(list(s) + list(set(imposedIndices) - set(s)))
    dlength = s.shape[0] - l1
    x = np.hstack((x,np.zeros(dlength)))

    print(TFormat.InBlue("Selection of "+\
        str(len(s))+" integration points (corresponding to "+str(round(100*\
        len(s)/numberOfIntegrationPoints, 5))+"% of the total)")); sys.stdout.flush()


    return s, x




def PrintReducedSchemeStatistics(s, x, integrands, integrals, normIntegrals):


    print(TFormat.InRed("Reduced Integration Scheme Constructed:"))

    if len(s) > 0:

        numberOfIntegrationPoints = integrands.shape[1]

        integrands_s = integrands[:,s]
        r = integrals - np.dot(integrands_s, x)
        err = np.linalg.norm(r)/normIntegrals

        print(TFormat.InRed("Relative error = "+str(err)+" obtained with " + \
        str(len(s))+" integration points (corresponding to " + \
        str(round(100*len(s)/numberOfIntegrationPoints, 5)) + "% of the total)"))
        print(TFormat.InRed("L0 norm for weight vector: " + str(len(s))))
        print(TFormat.InRed("L1 norm for weight vector: " + str(np.linalg.norm(x, 1))))
        print(TFormat.InRed("L2 norm for weight vector: " + str(np.linalg.norm(x, 2))))

    else:

        print("empty reduced integration scheme")


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

