# coding: utf-8

from Mordicus.Core.Containers.SolutionStructures.SolutionStructureBase import SolutionStructureBase
    
class MEDAsterSolutionStructure(SolutionStructureBase):
    """
    Class containing the information to contextualize a vector as a solution
    to MED format from a Code_Aster computation

    Attributes
    ----------
    __storage: list(MEDCouplingFieldDouble)
        contains a list of MEDCouplingFieldDouble, one for each relative level of element dimension (levelRemativeToMax)
    mesh: MEDFileUMesh
        global mesh used to read/write the solution
    """
    
    def GetNumberOfNodes(self):
        """Override method of base class"""
        sampleFields = [f[0] for f in self.GetInternalStorage().values()]
        numberOfPoints = 0
        for sampleField in sampleFields:
            numberOfPoints = numberOfPoints + sampleField.getNumberOfTuples()
        return numberOfPoints
    
    def GetNumberOfComponents(self):
        """Override method of base class"""
        sampleField, _ = next(v for v in self.GetInternalStorage().values())
        return sampleField.getNumberOfComponents()