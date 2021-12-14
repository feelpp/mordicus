# -*- coding: utf-8 -*-

import pickle
from mpi4py import MPI



def UpdateFileName(fileName):
    """
    Appends filename with numbering in case of parallel execution

    Parameters
    ----------
    fileName : str
        name of the file on disk

    Returns
    -------
    str
    """

    if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
        fileName += "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3)

    return fileName



def SaveState(fileName, obj):
    """
    Saves the data structure on disk

    Parameters
    ----------
    fileName : str
        name of the file on disk
    obj : custom_data_format
        object to save on disk
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

    Returns
    -------
    custom_data_format
    """
    inputName = UpdateFileName(fileName) + ".pkl"

    return pickle.load(open(inputName, "rb"))



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


