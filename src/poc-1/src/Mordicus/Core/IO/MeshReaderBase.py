# -*- coding: utf-8 -*-
import numpy as np


class MeshReaderBase(object):
    """
    Class containing the MeshReaderBase associated to a HF mesh file
    """

    def __init__(self):
        pass

    def ReadMesh(self):
        """
        Reads the mesh of the HF computation
                    
        Returns
        -------
        MeshBase
            mesh in one of the formats defined in Containers.Meshes
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover

    def __str__(self):
        res = "I am a MeshReaderBase, try instanciating a particular reader instead"
        return res
