# -*- coding: utf-8 -*-

import pickle
from mpi4py import MPI



def UpdateFileName(fileName):
    """
    1
    """

    if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
        fileName += "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3)

    return fileName



def SaveState(fileName, obj):
    """
    1
    """
    outputName = UpdateFileName(fileName) + ".pkl"

    output = open(outputName, "wb")
    pickle.dump(obj, output)
    output.close()



def LoadState(fileName):
    """
    Read the data structure from disk

    Parameters
    ----------
    fileName : str
        name of the file on disk
    """
    inputName = UpdateFileName(fileName) + ".pkl"

    return pickle.load(open(inputName, "rb"))



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


