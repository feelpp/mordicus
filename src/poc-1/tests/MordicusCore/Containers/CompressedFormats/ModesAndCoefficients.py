# -*- coding: utf-8 -*-
from MordicusCore.Containers.CompressedFormats import ModesAndCoefficients as MAC
import numpy as np


def test():

    modes = np.zeros((3, 12))
    times = np.zeros(7)
    coefficients = np.zeros((7, 3))
    compressedSnapshots = MAC.ModesAndCoefficients("toto", times, 1, True)
    compressedSnapshots.SetModes(modes)
    compressedSnapshots.SetCoefficients(coefficients)
    compressedSnapshots.GetTimes()
    compressedSnapshots.GetCoefficients()
    compressedSnapshots.GetModes()
    compressedSnapshots.GetNumberOfSnapshots()
    compressedSnapshots.GetNumberOfModes()
    compressedSnapshots.CheckDimensionsConsistence()
    compressedSnapshots.GetNbeOfComponents()
    compressedSnapshots.GetPrimality()
    compressedSnapshots.GetNumberOfDOFs()
    compressedSnapshots.GetNumberOfModes()
    compressedSnapshots.GetNumberOfNodes()
    print(compressedSnapshots)
    return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
