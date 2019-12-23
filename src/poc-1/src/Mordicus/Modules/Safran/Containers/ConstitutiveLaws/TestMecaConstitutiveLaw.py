# -*- coding: utf-8 -*-

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase
import numpy as np


class TestMecaConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a TestMecaConstitutiveLaw ONLY 3D

    Attributes
    ----------
    constitutiveLawVariables : dict
        dictionary with variable names (str) as keys and variables as type
    density : float
        density of the material
    """

    def __init__(self, set):
        assert isinstance(set, str)
        
        super(TestMecaConstitutiveLaw, self).__init__(set, "mechanical")

        self.constitutiveLawVariables = {}
        self.constitutiveLawVariables['nstatv'] = 0
        self.constitutiveLawVariables['ddsdde'] = np.array([[403846.15384615, 173076.92307692, 173076.92307692,      0.,       0.,         0.], [173076.92307692, 403846.15384615, 173076.92307692,      0.,       0.,         0.], [173076.92307692, 173076.92307692, 403846.15384615,      0.,       0.,         0.], [0.,              0.,              0.,         115384.61538462,      0.,       0.], [0.,              0.,              0.,              0.,  115384.61538462,      0.], [0.,              0.,              0.,              0.,       0.,         115384.61538462]])
        
        self.constitutiveLawVariables['flux'] = ['sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']
        self.constitutiveLawVariables['grad'] = ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31']
        self.constitutiveLawVariables['var_int'] = []
        self.constitutiveLawVariables['var_aux'] = []
        self.constitutiveLawVariables['var_extra'] = []
        
        self.constitutiveLawVariables['var'] = self.constitutiveLawVariables['grad'] + self.constitutiveLawVariables['flux']
        
        self.density = 8.6E-09
        

        
    def GetConstitutiveLawVariables(self):
    
        return self.constitutiveLawVariables
    


    def SetOneConstitutiveLawVariable(self, var, value):
        
        self.constitutiveLawVariables[var] = value
        
        
        
    def GetOneConstitutiveLawVariable(self, var):
    
        return self.constitutiveLawVariables[var]

    
        
    def GetDensity(self):
        
        return self.density

    
    def ComputeConstitutiveLaw(self):
        

        self.constitutiveLawVariables['stress'] = np.dot(self.constitutiveLawVariables['ddsdde'], self.constitutiveLawVariables['stran'])



    def GetIdentifier(self):
        """
        Returns
        -------
        couple of strings (set, type)
            the identifier of constitutive law
        """
        return self.set
    

    def __str__(self):
        res = "TestMecaConstitutiveLaw on set "+self.set
        return res
