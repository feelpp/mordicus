from os import path as osp
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
import feelpp

class FeelppSolutionReader(SolutionReaderBase):

    def __init__(self, mesh, space="Pch", order=1):
        self.Xh = feelpp.functionSpace(mesh.GetInternalStorage(), space, order)
        
    def ReadSnapshotComponent(self, fieldName, time=0, primality=True):
        u = self.Xh.element()
        u.load(fieldName,"")
        up = u.to_petsc().vec()
        #assert(u.size() == up.getSize())
        return up[:]
        return up.getArray() # should use this to avoid copy but currently crash

    def WriteSolution(self, fileName, solution, fieldStructure=None, fieldName="", nameInFile=None, append=False):
        b = feelpp.Backend(feelpp.Environment.worldCommPtr())
        v = b.newVector(self.Xh.mapPtr())
        assert(solution.shape[0] == v.size())
        for i in range(solution.shape[0]):
            v.set(i, solution[i])
        u = self.Xh.elementFromVec(v,0)
        path, name = osp.split(fileName)
        u.save(path, name)
