# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.BasicAlgorithms import SVD as SVD


def test():

    Mat = np.random.rand(10, 10)
    Mat[np.triu_indices(10, 1)] = 0.0

    SVD.TruncatedSVDSymLower(Mat, 1.0e-6)
    SVD.TruncatedSVDSymLower(Mat, nbModes = 5)

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
