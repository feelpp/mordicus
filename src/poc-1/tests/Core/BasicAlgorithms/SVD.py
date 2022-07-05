# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.BasicAlgorithms import SVD as SVD


def test():

    Mat = np.arange(9).reshape(3, 3)
    Mat[np.triu_indices(3, 1)] = 0.0

    ref = (np.array([16.01240515]), np.array([[-0.38252793],[-0.53464575],[-0.7535425 ]]))


    res = SVD.TruncatedSVDSymLower(Mat)
    np.testing.assert_almost_equal(res[0], ref[0])
    np.testing.assert_almost_equal(res[1], ref[1])


    res = SVD.TruncatedSVDSymLower(Mat, 1.0e-6)
    np.testing.assert_almost_equal(res[0], ref[0])
    np.testing.assert_almost_equal(res[1], ref[1])


    res = SVD.TruncatedSVDSymLower(Mat, nbModes = 5)
    np.testing.assert_almost_equal(res[0], ref[0])
    np.testing.assert_almost_equal(res[1], ref[1])


    res = SVD.TruncatedSVDSymLower(Mat, nbModes = 11)
    np.testing.assert_almost_equal(res[0], ref[0])
    np.testing.assert_almost_equal(res[1], ref[1])

    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
