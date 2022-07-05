

def run():



    import numpy as np
    import time

    from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR

    ngauss = 1

    ZmatLaw = ZIR.ConstructOneMechanicalConstitutiveLaw("./", "mat", "gen_evp", density = 1.e-8, set = "ALLELEMENT")


    temperature = 293.15 + np.zeros(ngauss)
    dtemp       = np.zeros(ngauss)
    stran = np.zeros((ngauss,6))
    dstran = np.zeros((ngauss,6))
    dstran[:,0] = 1.
    dstran[:,1] = 2.
    dstran[:,2] = 3.
    dstran[:,3] = 4.
    dstran[:,4] = 5.
    dstran[:,5] = 6.

    dstran[:,:] *= 0.001

    nstatev = ZmatLaw.GetOneConstitutiveLawVariable("nstatv")
    statev = np.zeros((ngauss,nstatev))

    print("statev =", statev)

    start = time.time()
    ddsdde1, stress1, statev = ZmatLaw.ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)
    durationZmat = time.time() - start

    print("ddsdde =", ddsdde1)
    print("stress =", stress1)
    print("statev =", statev)


    print("var names: ", ZmatLaw.GetOneConstitutiveLawVariable("var"))
    print("statev =", statev[0,:])
    print("p =", statev[0,-7])

    print("=======")

    """
    from tfel.material import ModellingHypothesis

    import mfront
    import mgis.behaviour as mgis_bv

    # Defining the modelling hypothesis
    h = mgis_bv.Hypothesis.TRIDIMENSIONAL
    # Loading the behaviour
    b = mgis_bv.load('src/libBehaviour.so','IsotropicLinearHardeningMises',h)


    # Setting the material data manager

    m = mgis_bv.MaterialDataManager(b, ngauss)

    print(type(m))


    E = 70000.
    nu = 0.3
    # yield strength
    sig0 = 250.
    Et = E/100.
    # hardening slope
    H = E*Et/(E-Et)

    for s in [m.s0, m.s1]:
        #mgis_bv.setMaterialProperty(s, "YoungModulus", E)
        #mgis_bv.setMaterialProperty(s, "PoissonRatio", nu)
        #mgis_bv.setMaterialProperty(s, "HardeningSlope", H)
        #mgis_bv.setMaterialProperty(s, "YieldStrength", sig0)
        #print("s =", s)
        #mgis_bv.setExternalStateVariable(s, "Temperature", 293.15)
        mgis_bv.setExternalStateVariable(s, "Temperature", np.array(ngauss*[293.15]), mgis_bv.MaterialStateManagerStorageMode.LocalStorage)



    m.s1.gradients[:,0] = 1.
    m.s1.gradients[:,1] = -0.5
    m.s1.gradients[:,2] = -0.5
    m.s1.gradients[:,3:] = 0.


    # integrate the behaviour
    it = mgis_bv.IntegrationType.IntegrationWithConsistentTangentOperator

    start = time.time()
    mgis_bv.integrate(m, it, 0, 0, m.n)
    durationMfront = time.time() - start

    print("sig =", m.s1.thermodynamic_forces)
    print("tgt mat =", m.K)
    #m.s1.internal_state_variables[:, -1]
    print("internal variable =", m.s1.internal_state_variables)
    #print("external variable =", m.s1.external_state_variables)
    print("internal variable p =", m.s1.internal_state_variables[:, -1])

    mgis_bv.update(m)
    """

    from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MfrontConstitutiveLaw as MCL

    MfrontLaw = MCL.MfrontConstitutiveLaw("ALLELEMENT")

    internalVariables = ['eel11', 'eel22', 'eel33', 'eel12', 'eel23', 'eel31', 'epcum']

    MfrontLaw.SetLawModelling('Tridimensional', 'IsotropicLinearHardeningMises', 'src/libBehaviour.so', internalVariables, ngauss)



    temperature = 293.15 + np.zeros(ngauss)
    dtemp       = np.zeros(ngauss)
    statev = 0.


    start = time.time()
    ddsdde2, stress2, statev = MfrontLaw.ComputeConstitutiveLaw(temperature, dtemp, stran, dstran, statev)
    durationMfront = time.time() - start

    print("ddsdde2 =", ddsdde2)
    print("stress2 =", stress2)
    print("statev =", MfrontLaw.m.s1.internal_state_variables)
    print("p =", statev[0,-1])

    print("===")
    print("rel diff stress =", np.linalg.norm(stress2-stress1)/np.linalg.norm(stress1))
    print("rel diff ddsdde =", np.linalg.norm(ddsdde2-ddsdde1)/np.linalg.norm(ddsdde1))

    print("===")
    print("duration Zmat =", durationZmat)
    print("duration Mfront =", durationMfront)


if __name__ == "__main__":

    run()

