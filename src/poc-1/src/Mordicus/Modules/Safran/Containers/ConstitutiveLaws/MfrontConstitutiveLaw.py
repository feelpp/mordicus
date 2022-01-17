# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

import os
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np
from Mordicus.Core.Containers.ConstitutiveLaws.ConstitutiveLawBase import ConstitutiveLawBase




class MfrontConstitutiveLaw(ConstitutiveLawBase):
    """
    Class containing a MfrontConstitutiveLaw

    Attributes
    ----------
    b : mgis.behaviour.Behaviour
        mfront behaviour
    m : mgis.behaviour.MaterialDataManager
        mfront material data manager
    density : float
        density of the material
    constitutiveLawVariables : dict
        dictionary with variable names (str) as keys and variables as type
    """

    def __init__(self, set):
        assert isinstance(set, str)

        super(MfrontConstitutiveLaw, self).__init__(set, "mechanical")

        self.b       = None
        self.m       = None
        self.density = None

        self.constitutiveLawVariables = {}
        self.constitutiveLawVariables['var'] = ['eto11', 'eto22', 'eto33', 'eto12', 'eto23', 'eto31', 'sig11', 'sig22', 'sig33', 'sig12', 'sig23', 'sig31']


    def SetConstitutiveLawVariables(self, constitutiveLawVariables):
        """
        Sets the constitutiveLawVariables dictionary

        Parameters
        ----------
        constitutiveLawVariables : dict
            dictionary with variable names (str) as keys and variables as type
        """
        self.constitutiveLawVariables = constitutiveLawVariables


    def SetOneConstitutiveLawVariable(self, var, value):
        """
        Sets one variable of the constitutive law

        Parameters
        ----------
        var : str
            name of the variable
        value : custom_data_structure
            variable of the constitutive law
        """
        self.constitutiveLawVariables[var] = value


    def SetDensity(self, density):
        """
        Sets the density of the constitutive law

        Parameters
        ----------
        density : float
            density of the material
        """
        self.density = density


    def GetDensity(self):
        """
        Returns the density of the material

        Returns
        -------
        float
            density
        """
        return self.density



    def GetConstitutiveLawVariables(self):
        """
        Returns
        -------
        dict
            complete dictionary defining the constitutive law variables
        """
        return self.constitutiveLawVariables


    def GetOneConstitutiveLawVariable(self, var):
        """
        Returns one variable of the constitutive law

        Parameters
        ----------
        var : str
            key of the dictionnary for storing the variable (e.g. name of the variable)

        Returns
        -------
        custom_data_structure
            variable of the constitutive law
        """
        return self.constitutiveLawVariables[var]


    def SetLawModelling(self, hypothesis, behavior, behaviorFile, internalVariables, nbIntPoints):
        """
        Sets the density of the constitutive law

        Parameters
        ----------
        hypothesis : mgis_bv.Hypothesis
            mfront hypothesis
        behavior : mgis.behaviour.Behaviour
            mfront behaviour
        behaviorFile : string
            path to compiled mfront behavior file (.so)
        internalVariables : list of strings
            list of the name of the internal variables modeling the constitutive law
        nbIntPoints : int
            number of integration points, where the constitutive law is modeled
        """

        import mgis.behaviour as mgis_bv
        availableHypothesis = {'Tridimensional': mgis_bv.Hypothesis.TRIDIMENSIONAL}

        assert hypothesis in availableHypothesis, "hypothesis '"+hypothesis+"' not available"

        h = availableHypothesis[hypothesis]
        self.b = mgis_bv.load(behaviorFile, behavior, h)
        self.m = mgis_bv.MaterialDataManager(self.b, nbIntPoints)

        self.constitutiveLawVariables['var'] += internalVariables
        self.constitutiveLawVariables['nstatv'] = len(internalVariables)


    def ComputeConstitutiveLaw(self, temperature, dtemp, stran, dstran, statev):
        """
        Main function of the class: computes a new material state using a constitutive law
        solver from a previous material state and variations of temperature and strain

        Parameters
        ----------
        temperature : np.ndarray or list
            temperature at the previous state, at integration points (np.ndarray of size (nbIntPoints) or list of length nbIntPoints)
        dtemp : np.ndarray or list
            variations of temperature between the previous state and the new state to compute,
            at integration points (np.ndarray of size (nbIntPoints) or list of length nbIntPoints)
        stran : np.ndarray
            strain at the previous state, at integration points (np.ndarray of size (nbIntPoints,nbeOfDualComponents))
        dstran : np.ndarray
            variations of strain between the previous state and the new state to compute,
            at integration points (np.ndarray of size (nbIntPoints,nbeOfDualComponents))
        statev : np.ndarray
            internal state variables at the previous state, at integration points (np.ndarray of size (nbIntPoints,nbeOfStateVariables))

        Returns
        -------
        np.ndarray
            of size (nbIntPoints, nbeOfDualComponents, nbeOfDualComponents) ddsdde: local tangent matrix at the new state
        np.ndarray
            of size (nbIntPoints, nbeOfDualComponents) stress: stress at the new state
        np.ndarray
            of size (nbIntPoints, nbeOfStateVariables) statev: internal state variables at the new state
        """

        import mgis.behaviour as mgis_bv

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
        """
        Updates the state of the internal variables
        """
        import mgis.behaviour as mgis_bv

        mgis_bv.update(self.m)


    def __str__(self):
        res = "Mechanical MfrontConstitutiveLaw on set "+self.set
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)