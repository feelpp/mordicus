from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
import feelpp

def ReadMesh(meshFileName):
    """
    Functional API
    
    Readsthe mesh defined in the Feelpp mesh file "meshFileName" (.geo, .msh, .json)
    
    Parameters
    ----------
    meshFileName : str
        mesh file
        
    Returns
    -------
    FeelppMesh
        mesh of the model
    """
    reader = FeelppMeshReader(meshFileName=meshFileName)
    return reader.ReadMesh()

class FeelppMeshReader(MeshReaderBase):
    """
    Class containing a reader for Feelpp mesh file
    
    Attributes
    ----------
    meshFileName : str
        name of the mesh file (.geo, .msh, .json)
    dim : int
        dimension of the mesh
    gorder : int
        order of the mesh
    realdim : int
        real dimension of the mesh
    h : double
        hsize of the mesh (for geo)
    """

    def __init__(self, meshFileName, dim=2, gorder=1, realdim=2, h=0.1):
        assert isinstance(meshFileName, str)
        assert feelpp.Environment.initialized

        super().__init__()
        self.meshFileName = meshFileName
        self.dim = dim
        self.gorder = gorder
        self.realdim = realdim
        self.h = h

    def ReadMesh(self):
        """
        Read the mesh
        
        Returns
        -------
        FeelppMesh
            mesh of the model
        """
        from Mordicus.Modules.Cemosis.Containers.Meshes import FeelppMesh
        mesh = feelpp.load(feelpp.mesh(dim=self.dim, geo=self.gorder, realdim=self.realdim), self.meshFileName, self.h)
        return FeelppMesh.FeelppMesh(mesh)



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)

