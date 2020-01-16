# -*- coding: utf-8 -*-
import numpy as np


def TimeInterpolation(time, timeIndices, vectors, vectorsMap = None):
    """
    Computes a time interpolation for temporal vectors defined either by
        - timeIndices  and vectors at these indices
        - or timeIndices, some tags at these time indices (vectorsMap), and vectors at those tags.
    
    Parameters
    ----------
    time : float
        the input time at which the interpolation is required
    timeIndices : np.ndarray
        the times where the available data is defined, of size
        (numberOfTimeIndices)
    vectors : np.ndarray or dict
        the available data, of size (numberOfVectors, numberOfDofs)
    vectorsMap : list, optional
        list containing the mapping from the numberOfTimeIndices times indices to the numberOfVectors vectors, of size (numberOfTimeIndices,). Default is None, in which case numberOfVectors = numberOfTimeIndices.
                
    Returns
    -------
    np.ndarray
        interpolated vector, of size (numberOfDofs)
    """
    
    timeIndices = np.array(timeIndices)

    if vectorsMap == None:
        vectorsMap = range(timeIndices.flatten().shape[0])

    if time <= timeIndices[0]:
        return vectors[vectorsMap[0]]
    if time >= timeIndices[-1]:
        return vectors[vectorsMap[-1]]

    previousTimeStep = np.where(timeIndices == timeIndices[timeIndices <= time].max())[
        0
    ][0]
    nextTimeStep = np.where(timeIndices == timeIndices[timeIndices >= time].min())[0][0]

    if previousTimeStep == nextTimeStep:
        return vectors[vectorsMap[previousTimeStep]]
    else:
        previousTime = timeIndices[previousTimeStep]
        nextTime = timeIndices[nextTimeStep]
        coef = (time - previousTime) / (nextTime - previousTime)

        return (
            coef * vectors[vectorsMap[nextTimeStep]]
            + (1 - coef) * vectors[vectorsMap[previousTimeStep]]
        )
