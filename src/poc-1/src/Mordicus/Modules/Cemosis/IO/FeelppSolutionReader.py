from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
import feelpp

class FeelppSolutionReader(SolutionReaderBase):

    def __init__(self, mesh, space="Pch", order=1):
        self.Xh = feelpp.functionSpace(mesh.GetInternalStorage(), space, order)
        
    def ReadSnapshotComponent(self, fieldName, time=0, primality=True):
        u = self.Xh.element()
        u.load(fieldName,"")
        return u.to_petsc().vec()[:]
