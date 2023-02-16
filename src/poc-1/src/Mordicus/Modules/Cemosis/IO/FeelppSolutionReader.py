from os import path as osp
import numpy as np
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
import feelpp

class FeelppSolutionReader(SolutionReaderBase):

    def __init__(self, mesh, space="Pch", order=1):
        self.mesh = mesh
        self.Xh = feelpp.functionSpace(mesh.GetInternalStorage(), space, order)

    def __init__(self, mesh, space):
        self.mesh = mesh
        self.Xh = space
        
    def ReadSnapshotComponent(self, fieldName, time=0, primality=True):
        u = self.Xh.element()
        u.load(fieldName,"")
        up = u.to_petsc().vec()
        #assert(u.size() == up.getSize())
        return up[:]
        return up.getArray() # should use this to avoid copy but currently crash

    def WriteSolution(self, fileName, solution, fieldStructure=None, fieldName="", nameInFile=None, append=False):
        """write solution to disk

        Args:
            fileName (_type_): name of the file
            solution (_type_): field to be saved
            fieldStructure (_type_, optional): _description_. Defaults to None.
            fieldName (str, optional): name of the field. Defaults to "".
            nameInFile (_type_, optional): _description_. Defaults to None.
            append (bool, optional): _description_. Defaults to False.
        """        
        b = feelpp.Backend(feelpp.Environment.worldCommPtr())
        v = b.newVector(self.Xh.mapPtr())
        assert(solution.shape[0] == v.size())
        for i in range(solution.shape[0]):
            v.set(i, solution[i])
        u = self.Xh.element(v,0)
        path, name = osp.split(fileName)
        #self.e.addP1c(name, u)
        u.save(path, name)

    def WriteReducedOrderBasis(self, fileName, solutionStructure, reducedOrderBasis, fieldName):
        self.e = feelpp.exporter(self.mesh, "reducedbasis", "change_coords_only")
        for i in range(reducedOrderBasis[fieldName].shape[0]):
            filepath = f"{fileName}_{i}.h5"
            self.WriteSolution(filepath, reducedOrderBasis[fieldName][i])
        #self.e.save()

    def ReadReducedOrderBasis(self, fileName, solutionStructure, fieldName):
        i = 0
        base = []
        while True:
            filepath = f"{fileName}_{i}.h5"
            try:
                base.append(self.ReadSnapshotComponent(filepath))
            except:
                break
        return {fieldName: np.concatenate(base, axis=0)}
