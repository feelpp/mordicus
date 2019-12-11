# -*- coding: utf-8 -*-
import numpy as np
from MordicusCore.Containers.BaseObject import BaseObject


class MeshReaderBase(BaseObject):
    """
    Class containing the MeshReaderBase associated to a HF mesh file
    """

    def __init__(self):
        super(MeshReaderBase, self).__init__()

    def ReadMesh(self):
        """
        Reads the mesh of the HF computation
                    
        Returns
        -------
        MeshBase
            mesh in one of the formats defined in Containers.Meshes
        """
        raise ("Not implemented in ReaderBase")  # pragma: no cover

    def __str__(self):
        res = "I am a MeshReaderBase, try instanciating a particular reader instead"
        return res
