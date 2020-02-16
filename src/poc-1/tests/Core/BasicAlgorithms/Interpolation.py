# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.BasicAlgorithms import Interpolation as TI


def test():

    timeIndices = np.array([0.0, 1.0, 2.5])
    vectors = np.array([np.ones(5), 2.0 * np.ones(5), 3.0 * np.ones(5)])
    vectorsDic = {}
    vectorsDic["vec1"] = np.ones(5)
    vectorsDic["vec2"] = 2.0 * np.ones(5)
    vectorsMap = ["vec1", "vec2", "vec1"]

    TI.PieceWiseLinearInterpolation(-1.0, timeIndices, vectors)
    TI.PieceWiseLinearInterpolation(3.0, timeIndices, vectorsDic, vectorsMap)
    TI.PieceWiseLinearInterpolation(1.0, timeIndices, vectors)
    TI.PieceWiseLinearInterpolation(1.0, timeIndices, vectorsDic, vectorsMap)
    TI.PieceWiseLinearInterpolation(0.4, timeIndices, vectors)
    TI.PieceWiseLinearInterpolation(1.4, timeIndices, vectors)
    TI.PieceWiseLinearInterpolation(0.6, timeIndices, vectorsDic, vectorsMap)


    timeIndices = [0.,  100.,  200.,  300.,  400.,  500.,  600.,  700.,  800.,  900., 1000., 2000.]
    coefficients = [2000000., 2200000., 2400000., 2000000., 2400000., 3000000., 2500000., 2400000.,
 2100000., 2800000., 4000000., 3000000.]


    res = []
    vals = [0., 100., 200., 300., 400., 500., 600., 700., 800., 900., 1000., 701.4752695491923]
    for val in vals:
        res.append(TI.PieceWiseLinearInterpolation(val, timeIndices, coefficients))

    res2 = TI.PieceWiseLinearInterpolationVectorized(np.array(vals), timeIndices, coefficients)



    testlist = np.array([0.0, 1.0, 2.5, 10.])
    valList = np.array([-1., 11., 0.6, 2.0, 2.6, 9.9, 1.0])

    res = np.empty(valList.shape[0], dtype = int)
    for i, val in enumerate(valList):
        res[i] = TI.BinarySearch(testlist, val)

    res2 = TI.BinarySearchVectorized(testlist, valList)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
