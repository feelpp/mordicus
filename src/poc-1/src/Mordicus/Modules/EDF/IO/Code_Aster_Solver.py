"""
Created on 26 févr. 2020

@author: Guilhem Ferté
"""
import os.path as osp
from Mordicus.Core.IO.ExternalSolvingProcedure import ExternalSolvingProcedure
from string import Template

class Code_Aster_Solver(ExternalSolvingProcedure):
    """
    Informations to call Code_Aster
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """
        return super(Code_Aster_Solver, self).__init__(**kwargs)