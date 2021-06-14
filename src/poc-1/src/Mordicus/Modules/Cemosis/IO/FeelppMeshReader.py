# -*- coding: utf-8 -*-
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
import feelpp
from pathlib import Path

def ReadMesh(meshFileName,dim=3,realdim=3):
    """
    Functional API

    Reads the mesh defined the Gmsh mesh file "meshFileName" (.msh)

    Parameters
    ----------
    meshFileName : str
        Gmsh mesh file
    dim: int 
        topological dimension of the mesh
    realdim: int
        real space dimension

    Returns
    -------
   FeelppUnstructuredMesh
        mesh of the HF computation
    """
    
    reader = FeelppMeshReader(meshFileName=meshFileName,dim=dim,realdim=realdim)
    return reader.ReadMesh()


class FeelppMeshReader(MeshReaderBase):
    """
    Class containing a reader for Gmsh mesh or a geo file

    Attributes
    ----------
    meshFileName : str
        name of the GMSH mesh file (.msh)
    """

    def __init__(self, meshFileName,dim,realdim):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        super(FeelppMeshReader, self).__init__()

        assert isinstance(meshFileName, str)

        folder = str(Path(meshFileName).parents[0])
        suffix = str(Path(meshFileName).suffix)  # .msh
        stem = str(Path(meshFileName).stem)  # mesh
        self.meshFileName = meshFileName
        self.m = feelpp.mesh(dim=dim,realdim=realdim)

    def ReadMesh(self):
        """
        Read the HF mesh

        Returns
        -------
        FeelppUnstructuredMesh
            mesh of the HF computation
        """
        self.m = feelpp.load(self.m, self.meshFileName, 0.1)
        if feelpp.Environment.isMasterRank():
            print("mesh ", self.m.dimension(), "D nelts:", self.m.numGlobalElements())
            print("mesh ", self.m.dimension(), "D nfaces:", self.m.numGlobalFaces())
            print("mesh ", self.m.dimension(), "D hmin:", self.m.hMin())
            print("mesh ", self.m.dimension(), "D havg:", self.m.hAverage())
            print("mesh ", self.m.dimension(), "D hmax:", self.m.hMax())
            print("mesh ", self.m.dimension(), "D measure:", self.m.measure())

        from Mordicus.Modules.Cemosis.Containers.Meshes import FeelppUnstructuredMesh as FUM
        return FUM.FeelppUnstructuredMesh(self.m)
