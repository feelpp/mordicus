# -*- coding: utf-8 -*-
import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np
#import mfront
import mgis.behaviour as mgis_bv

from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase


availableHypothesis = {'Tridimensional': mgis_bv.Hypothesis.TRIDIMENSIONAL}



class MfrontConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a MfrontConstitutiveLaw

    Attributes
    ----------
    density : float
        density of the material
    constitutiveLawVariables : dict
        dictionary with variable names (str) as keys and variables as type
    m : mgis.behaviour.MaterialDataManager
        mfront material data manager
    b : mgis.behaviour.Behaviour
        mfront behaviour
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(MfrontConstitutiveLaw, self).__init__(set, "mechanical")

        self.density = None
        self.b       = None
        self.m       = None

        self.constitutiveLawVariables = {}

        self.constitutiveLawVariables['var'] = ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31', 'sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']


    def SetConstitutiveLawVariables(self, constitutiveLawVariables):

        self.constitutiveLawVariables = constitutiveLawVariables


    def SetOneConstitutiveLawVariable(self, var, value):

        self.constitutiveLawVariables[var] = value


    def SetDensity(self, density):
        self.density = density


    def GetDensity(self):
        return self.density



    def GetConstitutiveLawVariables(self):

        return self.constitutiveLawVariables


    def GetOneConstitutiveLawVariable(self, var):

        return self.constitutiveLawVariables[var]


    def SetLawModelling(self, hypothesis, behavior, behaviorFile, internalVariables, nbIntPoints):

        assert hypothesis in availableHypothesis, "hypothesis '"+hypothesis+"' not available"

        h = availableHypothesis[hypothesis]
        self.b = mgis_bv.load(behaviorFile, behavior, h)
        self.m = mgis_bv.MaterialDataManager(self.b, nbIntPoints)

        self.constitutiveLawVariables['var'] += internalVariables
        self.constitutiveLawVariables['nstatv'] = len(internalVariables)


    def ComputeConstitutiveLaw(self, temperature, dtemp, stran, dstran, statev):

        mgis_bv.setExternalStateVariable(self.m.s0, "Temperature", temperature, mgis_bv.MaterialStateManagerStorageMode.LocalStorage)
        mgis_bv.setExternalStateVariable(self.m.s1, "Temperature", temperature + dtemp, mgis_bv.MaterialStateManagerStorageMode.LocalStorage)

        self.m.s0.gradients[:,:] = stran
        self.m.s1.gradients[:,:] = stran + dstran

        self.m.s0.gradients[:,3:] /= np.sqrt(2.)
        self.m.s1.gradients[:,3:] /= np.sqrt(2.)

        it = mgis_bv.IntegrationType.IntegrationWithConsistentTangentOperator
        mgis_bv.integrate(self.m, it, 0, 0, self.m.n)

        stress = self.m.s1.thermodynamic_forces
        ddsdde = self.m.K

        stress[:,3:]   /= np.sqrt(2.)
        ddsdde[:,3:,:] /= np.sqrt(2.)
        ddsdde[:,:,3:] /= np.sqrt(2.)

        statev = self.m.s1.internal_state_variables

        return ddsdde, stress, statev

    def UpdateInternalState(self):

        mgis_bv.update(self.m)


    def __str__(self):
        res = "Mechanical MfrontConstitutiveLaw on set "+self.set
        return res
