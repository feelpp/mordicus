# -*- coding: utf-8 -*-
import numpy as np


def PieceWiseLinearInterpolation(item, itemIndices, vectors, vectorsMap = None):
    """
    Computes a item interpolation for temporal vectors defined either by
        - itemIndices  and vectors at these indices
        - or itemIndices, some tags at these item indices (vectorsMap), and vectors at those tags.

    Parameters
    ----------
    item : float
        the input item at which the interpolation is required
    itemIndices : np.ndarray
        the items where the available data is defined, of size
        (numberOfTimeIndices)
    vectors : np.ndarray or dict
        the available data, of size (numberOfVectors, numberOfDofs)
    vectorsMap : list, optional
        list containing the mapping from the numberOfTimeIndices items indices to the numberOfVectors vectors, of size (numberOfTimeIndices,). Default is None, in which case numberOfVectors = numberOfTimeIndices.

    Returns
    -------
    np.ndarray
        interpolated vector, of size (numberOfDofs)
    """
    item = float(item)
    itemIndices = np.array(itemIndices)

    if vectorsMap == None:
        vectorsMap = range(itemIndices.flatten().shape[0])

    if item <= itemIndices[0]:
        return vectors[vectorsMap[0]]
    if item >= itemIndices[-1]:
        return vectors[vectorsMap[-1]]

    first = 0
    last = len(itemIndices)-1

    approxFromBelow = None

    while first<=last:
        midpoint = (first + last)//2
        if itemIndices[midpoint] == item:
            return vectors[vectorsMap[midpoint]]
        else:
            if item <= itemIndices[midpoint]:
                last = midpoint-1
                approxFromBelow = True
            else:
                first = midpoint+1
                approxFromBelow = False


    if approxFromBelow == True:
        prev = midpoint-1
    else:
        prev = midpoint

    previousTime = itemIndices[prev]
    nextTime = itemIndices[prev+1]
    coef = (item - previousTime) / (nextTime - previousTime)
    return (
            coef * vectors[vectorsMap[prev+1]]
            + (1 - coef) * vectors[vectorsMap[prev]]
        )


def BinarySearch(list, item):
    """
    Searches in the sorted data "list" the rank of the largest element smaller than item, in log(len(list)) complexity

    Parameters
    ----------
    list: list or one-dimensional np.ndarray
        the sorted data from which the previous rank is searched
    item : float or int
        the item for which the previous rank is searched

    Returns
    -------
    int
        the rank of the largest element smaller than item in the sorted data "list"
    """
    first = 0
    last = len(list)-1
    res = None

    if item < list[first]:
        return first

    if item > list[last]:
        return last

    while first<=last:
        midpoint = (first + last)//2
        if list[midpoint] == item:
            return midpoint
        else:
            if item <= list[midpoint]:
                last = midpoint-1
                res = midpoint-1
            else:
                first = midpoint+1
                res = midpoint

    return res


def PieceWiseLinearInterpolationVectorized(items, itemIndices, vectors, vectorsMap = None):
    """
    Vectorized version of PieceWiseLinearInterpolation (items is now a list or one-dimensional np.ndarray)

    Parameters
    ----------
    items : list or one-dimensional np.ndarray
        the input items at which the interpolation is required
    itemIndices : np.ndarray
        the items where the available data is defined, of size
        (numberOfTimeIndices)
    vectors : np.ndarray or dict
        the available data, of size (numberOfVectors, numberOfDofs)
    vectorsMap : list, optional
        list containing the mapping from the numberOfTimeIndices items indices to the numberOfVectors vectors, of size (numberOfTimeIndices,). Default is None, in which case numberOfVectors = numberOfTimeIndices.

    Returns
    -------
    np.ndarray
        interpolated vector, of size (numberOfDofs)
    """

    itemIndices = np.array(itemIndices)
    items = np.array(items)
    vectors = np.array(vectors)

    if vectorsMap == None:
        vectorsMap = np.arange(itemIndices.flatten().shape[0])

    prev = BinarySearchVectorized(itemIndices, items)

    previousTime = itemIndices[prev]
    nextTime = itemIndices[prev+1]

    coef = np.divide(items - previousTime, nextTime - previousTime)

    #coef = [(items[i] - previousTime[i]) / (nextTime[i] - previousTime[i]) for i in range(items.shape[0])]

    res = np.multiply(coef, vectors[vectorsMap[prev+1]]) + np.multiply((1-coef),vectors[vectorsMap[prev]])

    #res = [coef[i] * vectors[vectorsMap[prev[i]+1]] + (1 - coef[i]) * vectors[vectorsMap[prev[i]]] for i in range(items.shape[0])]
    #res = np.array(res)

    res[items <= itemIndices[0]]  = vectors[vectorsMap[0]]
    res[items >= itemIndices[-1]] = vectors[vectorsMap[-1]]

    return res



def BinarySearchVectorized(list, items):
    """
    Vectorized version of BinarySearch (items is now a list or one-dimensional np.ndarray)

    Parameters
    ----------
    list: list or one-dimensional np.ndarray
        the sorted data from which the previous rank is searched
    item : list or one-dimensional np.ndarray
        the items for which the previous ranks are searched

    Returns
    -------
    int
        the rank of the largest element smaller than item in the sorted data "list"
    """

    items = np.array(items)
    last = len(list)-1
    res = np.empty(items.shape, dtype = int)

    arange = np.arange(len(items))
    remainingIndices = np.arange(len(items))


    localIndices1 = items <= list[0]
    indices = arange[localIndices1]
    res[indices] = 0

    localIndices2 = items >= list[last]
    indices = arange[localIndices2]
    res[indices] = last

    remainingIndices = arange[np.invert(localIndices1) & np.invert(localIndices2)]


    first = np.zeros(items.shape)
    last  = (len(list)-1)+np.zeros(items.shape, dtype = int)


    while remainingIndices.shape[0]>0:

        localFirst = first[remainingIndices]
        localLast = last[remainingIndices]

        localItems = items[remainingIndices]
        localArange = arange[remainingIndices]

        midpoint = ((localFirst + localLast)//2).astype(int)

        listCheck = list[midpoint]

        localIndices1 = localItems == listCheck
        localIndices2 = localItems < listCheck
        localIndices3 = localItems > listCheck


        indices = localArange[localIndices1]
        res[indices] = midpoint[localIndices1]

        indices = localArange[localIndices2]
        last[indices] = res[indices] = midpoint[localIndices2] - 1

        indices = localArange[localIndices3]
        temp = midpoint[localIndices3]
        first[indices] = temp + 1
        res[indices]  = temp

        remainingIndices = localArange[np.invert(localIndices1) & (localLast>=localFirst)]


    return res



