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