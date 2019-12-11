# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.BasicAlgorithms import TimeInterpolation as TI


def test():

    timeIndices = np.array([0.0, 1.0, 2.5])
    vectors = np.array([np.ones(5), 2.0 * np.ones(5), 3.0 * np.ones(5)])
    vectorsDic = {}
    vectorsDic["vec1"] = np.ones(5)
    vectorsDic["vec2"] = 2.0 * np.ones(5)
    vectorsMap = ["vec1", "vec2", "vec1"]

    TI.TimeInterpolation(-1.0, timeIndices, vectors)
    TI.TimeInterpolation(3.0, timeIndices, vectorsDic, vectorsMap)
    TI.TimeInterpolation(1.0, timeIndices, vectors)
    TI.TimeInterpolation(1.0, timeIndices, vectorsDic, vectorsMap)
    TI.TimeInterpolation(0.4, timeIndices, vectors)
    TI.TimeInterpolation(0.6, timeIndices, vectorsDic, vectorsMap)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
