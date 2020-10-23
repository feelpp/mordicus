# -*- coding: utf-8 -*-
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np


class MeshBase(object):
    """
    Class containing a MeshBase, with an internal storage hidden to all its children classes

    Attributes
    ----------
    __storage : typeToDefine
    """

    def __init__(self):
        self.__storage = None


    def SetInternalStorage(self, __storage):
        """
        Sets the internal storage

        Parameters
        ----------
        __storage : typeToDefine
        """
        if self.__storage is not None:
            print(
                "Internal storage already set. Replacing it anyway."
            )  # pragma: no cover
        self.__storage = __storage

    def GetInternalStorage(self):
        """
        Returns
        -------
        typeToDefine
            internal storage
        """
        if self.__storage is None:
            raise AttributeError("Please set internal storage")  # pragma: no cover
        return self.__storage


    def GetNodes(self):
        """
        Returns
        -------
        np.ndarray
            nodes of the mesh, of size (numberOfNodes,dimensionality)
        """
        print(
            "WARNING: I am a MeshBase! Try instanciating a particular mesh instead. Returning an empty np.ndarray"
        )
        return np.empty((0, 0))

    def AllElementsIterator(self):
        """
        Constructs an iterator over all the elements of the mesh.
        An element is np.ndarray of size (numberOfNodes,dimensionality)
        containing the indices of the nodes included in this element

        Returns
        -------
        iterator
            an iterator over all the elements of the mesh
        """
        raise NotImplementedError("Not implemented in MeshBase")  # pragma: no cover

    def GetNumberOfNodes(self):
        """
        Returns
        -------
        int
            the number of nodes of the mesh
        """
        return self.GetNodes().shape[0]

    def GetDimensionality(self):
        """
        Returns
        -------
        int
            the dimensionality of the mesh
        """
        return self.GetNodes().shape[1]


    def GetElemAttach(self, node_rk: int) -> list:
        """
        Return the list of all elements ranks (the index in the full element list )
        attach to a given node

        Arguments:
            node_rk {int} -- the rank of the node

        Returns:
            list -- the list of all elements attach to the input node
        """
        raise Exception("Not implemented in mesh base") # pragma: no cover

    def GetElemContaining(self, ip_rk: int) -> int:
        """
        Return the rank of the element containint the given integration point

        Arguments:
            ip_rk {int} -- the rank of the integration point to locate, i.e. the index of this integration point in the full list of ip.

        Returns:
            int -- the rank of the element containing the input integration point
        """
        raise Exception("Not implemented in mesh base") # pragma: no cover

    def __str__(self):
        res = "I am a MeshBase, try instanciating a particular mesh instead"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


