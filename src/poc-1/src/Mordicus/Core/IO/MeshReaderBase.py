# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#



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


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


