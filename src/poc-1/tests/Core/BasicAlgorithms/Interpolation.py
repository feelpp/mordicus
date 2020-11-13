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
    TI.PieceWiseLinearInterpolationWithMap(3.0, timeIndices, vectorsDic, vectorsMap)
    TI.PieceWiseLinearInterpolation(1.0, timeIndices, vectors)
    TI.PieceWiseLinearInterpolationWithMap(1.0, timeIndices, vectorsDic, vectorsMap)
    TI.PieceWiseLinearInterpolation(0.4, timeIndices, vectors)
    TI.PieceWiseLinearInterpolation(1.4, timeIndices, vectors)
    TI.PieceWiseLinearInterpolationWithMap(0.6, timeIndices, vectorsDic, vectorsMap)
    TI.PieceWiseLinearInterpolationVectorizedWithMap(np.array([-0.1, 2.0, 3.0]), timeIndices, vectorsDic, vectorsMap)


    timeIndices = np.array([0., 100., 200.,  300.,  400.,  500.,  600.,  700.,\
                            800.,  900., 1000., 2000.])
    coefficients = np.array([2000000., 2200000., 2400000., 2000000., 2400000.,\
                             3000000., 2500000., 2400000., 2100000., 2800000.,\
                             4000000., 3000000.])


    vals = np.array([-10., 0., 100., 150., 200., 300., 400., 500., 600., 700.,\
                     800., 900., 1000., 3000., 701.4752695491923])


    res = np.array([2000000., 2000000., 2200000., 2300000., 2400000., 2000000.,\
                    2400000., 3000000., 2500000., 2400000., 2100000., 2800000.,\
                    4000000., 3000000., 2395574.19135242])

    for i in range(vals.shape[0]):
        assert (TI.PieceWiseLinearInterpolation(vals[i], timeIndices, coefficients) - res[i])/res[i] < 1.e-10



    TI.PieceWiseLinearInterpolationVectorized(np.array(vals), timeIndices, coefficients)



    testlist = np.array([0.0, 1.0, 2.5, 10.])
    valList = np.array([-1., 11., 0.6, 2.0, 2.6, 9.9, 1.0])

    ref = np.array([0, 3, 0, 1, 2, 2, 1], dtype = np.int)
    res = TI.BinarySearchVectorized(testlist, valList)

    for i, val in enumerate(valList):
        assert TI.BinarySearch(testlist, val) == ref[i]
        assert res[i] == ref[i]



    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
