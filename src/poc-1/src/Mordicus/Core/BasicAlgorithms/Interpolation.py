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
import bisect




def BinarySearch(orderedList, item):
    """
    Inspects the sorted list "ordered_list" and returns:
        - 0 if item <= orderedList[0]
        - the rank of the largest element smaller or equal than item otherwise

    Parameters
    ----------
    ordered_list: list or one-dimensional np.ndarray
        the data sorted in increasing order from which the previous rank is\
        searched
    item : float or int
        the item for which the previous rank is searched

    Returns
    -------
    int
        0 or the rank of the largest element smaller or equal than item in\
        "orderedList"
    """
    return max(bisect.bisect_right(orderedList, item) - 1, 0)



def BinarySearchVectorized(orderedList, items):
    """
    Vectorized version of BinarySearch (items is now a list or one-dimensional np.ndarray)
    """
    return np.fromiter(map(lambda item: BinarySearch(orderedList, item), items), dtype = np.int)



def PieceWiseLinearInterpolation(item, itemIndices, vectors):
    """
    Computes a item interpolation for temporal vectors defined either by
    itemIndices  and vectors at these indices

    Parameters
    ----------
    item : float
        the input item at which the interpolation is required
    itemIndices : np.ndarray
        the items where the available data is defined, of size
        (numberOfTimeIndices)
    vectors : np.ndarray or dict
        the available data, of size (numberOfVectors, numberOfDofs)

    Returns
    -------
    np.ndarray
        interpolated vector, of size (numberOfDofs)
    """

    if item <= itemIndices[0]:
        return vectors[0]
    if item >= itemIndices[-1]:
        return vectors[-1]


    prev = BinarySearch(itemIndices, item)
    coef = (item - itemIndices[prev]) / (itemIndices[prev+1] - itemIndices[prev])

    return (
            coef * vectors[prev+1]
            + (1 - coef) * vectors[prev]
        )


def PieceWiseLinearInterpolationWithMap(item, itemIndices, vectors, vectorsMap):
    """
    Computes a item interpolation for temporal vectors defined either by
    itemIndices, some tags at these item indices (vectorsMap), and vectors at those tags.

    Parameters
    ----------
    item : float
        the input item at which the interpolation is required
    itemIndices : np.ndarray
        the items where the available data is defined, of size
        (numberOfTimeIndices)
    vectors : np.ndarray or dict
        the available data, of size (numberOfVectors, numberOfDofs)
    vectorsMap : list
        list containing the mapping from the numberOfTimeIndices items indices to the numberOfVectors vectors, of size (numberOfTimeIndices,). Default is None, in which case numberOfVectors = numberOfTimeIndices.

    Returns
    -------
    np.ndarray
        interpolated vector, of size (numberOfDofs)
    """


    if item <= itemIndices[0]:
        return vectors[vectorsMap[0]]
    if item >= itemIndices[-1]:
        return vectors[vectorsMap[-1]]


    prev = BinarySearch(itemIndices, item)

    coef = (item - itemIndices[prev]) / (itemIndices[prev+1] - itemIndices[prev])

    return (
            coef * vectors[vectorsMap[prev+1]]
            + (1 - coef) * vectors[vectorsMap[prev]]
        )



def PieceWiseLinearInterpolationVectorized(items, itemIndices, vectors):
    """
    Vectorized version of PieceWiseLinearInterpolation (items is now a list or one-dimensional np.ndarray)
    """
    return [PieceWiseLinearInterpolation(item, itemIndices, vectors) for item in items]
    #return np.fromiter(map(lambda item: PieceWiseLinearInterpolation(item, itemIndices, vectors), items), dtype = type(vectors[0]))



def PieceWiseLinearInterpolationVectorizedWithMap(items, itemIndices, vectors, vectorsMap):
    """
    Vectorized version of PieceWiseLinearInterpolation (items is now a list or one-dimensional np.ndarray)
    """
    return [PieceWiseLinearInterpolationWithMap(item, itemIndices, vectors, vectorsMap) for item in items]
    #return np.fromiter(map(lambda item: PieceWiseLinearInterpolationWithMap(item, itemIndices, vectors, vectorsMap), items), dtype = np.float)




if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


