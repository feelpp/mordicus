import os
import os.path as osp
import numpy as np
import math

from Mordicus.Modules.EDF.IO.SolvingProcedures import Solver_Code_Aster
from Mordicus.Modules.EDF.IO.Readers import MEDMeshReader
from Mordicus.Modules.EDF.Loadings import KinematicConditions

from Mordicus.Core.IO.SolverDataset import SolverDataset
from Mordicus.Core.IO.FixedData import FixedData

from Mordicus.Core.Containers import (ProblemData, Solution)
from Mordicus.Core.DataCompressors import ComputeReducedOrderBasisFromCollectionProblemData
from Mordicus.Core.OperatorCompressors import EmpiricalQuadrature as EQ
from Mordicus.Core.DataCompressors import SnapshotPOD as SP

from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP

# ------------------------------------------------------------------
# COMPUTATION OF CONSTANT DATA FOR THE HF AND REDUCED CASE
# ------------------------------------------------------------------

root_to_all = sp.join(osp.dirname(osp.abspath(__file__)), "data")

# Definition of the solver -> NEW OBJECT
# --------------------------------------
call_script = """
{solver_install}/bin/as_run --vers={solver_version} {input_root_folder}/{input_main_file}
"""

# Environment variables at the solver level
solver_cfg = {"solver_version" : "/home/A34370/dev/codeaster/install/std/share/aster",
              "solver_install" : "/opt/salome-meca/2019/V2019.0.3_scibian_9/tools/Code_aster_frontend-20190"
              }

external_solver = Solver_Code_Aster(solver_cfg=sover_cfg,
                                    solver_call_procedure_type="shell",
                                    call_script=call_script)

# Definition of the solver dataset -> NEW OBJECT
# ----------------------------------------------
input_data = {"input_root_folder" : osp.join(root_to_all, "step1"),
              "input_main_file"   : "case.export",
              "input_result_path" : "base",
              "input_result_type" : "folder"}

# Should InitialCondition, Loadings and ConstitutiveLaw derive from FixedData
solver_dataset = SolverDataset(FixedData,
                               external_solver,
                               input_data)
fixed_data = solver_dataset.run()

# Read mesh -> REUSE EXISTING API
# -------------------------------

# Safran also offers static method MEDMeshReader.ReadMesh(meshFilename)
# The latter is chosen cause it retains the mesh path
reader_instance = MEDMeshReader(med_filename)
mesh = reader_instance.ReadMesh()

# EXTEND API: get Gauss points and total Volume
coor_elem_ref = [-1.e0, -1.e0, -1.e0, +1.e0, -1.e0, -1.e0, +1.e0, +1.e0, -1.e0, -1.e0, +1.e0, -1.e0, -1.e0, -1.e0, +1.e0, +1.e0, -1.e0, +1.e0, +1.e0, +1.e0, +1.e0, -1.e0, +1.e0, +1.e0, 0.e0, -1.e0, -1.e0, +1.e0,  0.e0, -1.e0, 0.e0, +1.e0, -1.e0, -1.e0,  0.e0, -1.e0, -1.e0, -1.e0,  0.e0, +1.e0, -1.e0,  0.e0, +1.e0, +1.e0,  0.e0, -1.e0, +1.e0,  0.e0, 0.e0, -1.e0, +1.e0, +1.e0,  0.e0, +1.e0, 0.e0, +1.e0, +1.e0, -1.e0,  0.e0, +1.e0]
a =  [-0.774596669241483e0, 0.e0, 0.774596669241483e0]
h =  [ 0.555555555555556e0, 0.888888888888889e0, 0.555555555555556e0]
weight_gauss = []
coor_gauss = []
for ix in range(3):
    for iy in range(3):
        for iz in range(3):
            weight_gauss.append(h[ix]*h[iy]*h[iz])
            coor_gauss.append(a[ix])
            coor_gauss.append(a[iy])
            coor_gauss.append(a[iz])
approx = ApproximationSpace("finite element", "P2-full",
                            coor_elem_ref,
                            coor_gauss,
                            weight_gauss=weight_gauss)
np_array_gauss_coor = mesh.gaussPointsCoordinates(element_group="PACE",
                                                  approximation_space=approx)
volume = mesh.getVolume(element_group="PACE")

# Get matrix B of kinematic conditions
# ------------------------------------
input_data = {"input_root_folder" : osp.join(root_to_all, "step2"),
              "input_main_file"   : "case.export",
              "input_result_path" : "matrix_B.npy",
              "input_result_type" : "matrix"}
solver_dataset = SolverDataset(ResolutionData,
                               external_solver,
                               input_data)
matrix_B = solver_dataset.run()

# Computation needed for the error estimate
# -----------------------------------------
matBT = matB.copy()
matBT = np.transpose(matBT)
matBBT = matB @ matBT

# ------------------------------------------------------------------
# DEFINE THE CASE DATA
# ------------------------------------------------------------------

# CaseData is split in 2: ProblemData and CollectionProblemData

# Defining a ProblemData and associated solutions
# The initialization of Solution contains some of the informations of OutputDescription
#    - returned_type  : not present yet, for now it is all "Field"
#    - field_structure: contains the infos in solutionName, nbeOfComponentsPrimal, numberOfNodes

# Define Solutions
# ----------------

# The displacement field is classical: same number of components per node
numberOfNodes         = mesh.GetNumberOfNodes()
nbeOfComponentsPrimal = 3
solutionU = S.Solution(quantity=("U", "displacement", "m"),
                       structure=(nbeOfComponentsPrimal, numberOfNodes),
                       primality=True)

# The sigma field is not classical, there is not the same number of components per Gauss Points
# There is a necessity of providing a numpy array for the component structure
numberOfIntegrationPoints = np_array_gauss_coor.shape[1]
solutionSigma = S.Solution(quantity="sigma",
                           structure=(vector_of_components, vector_of_points),
                           primality=False)

# Define ProblemData
# ------------------
problemData = PD.ProblemData(root_to_all,
                             reference_support=mesh)
problemData.AddSolution(solutionU)
problemData.AddSolution(solutionSigma)

# Define collectionProblemData
# ----------------------------

# CollectionProblemData: existing API
collectionProblemData = CPD.CollectionProblemData()

# addProblemData to populate -> declareReferenceProblemData to declare a structure
collectionProblemData.declareReferenceProblemData(problemData)

# CollectionProblemData: extend the API, define parameters and indexation
collectionProblemData.declareParameters(("p_etard", "p_etaid"),
                                        quantity=("damping", "viscosity", "Pa.s"),
                                        description=("recoverable creep coefficient",
                                                     "non recoverable creep coefficient"))

# Using np.meshgrid to define a cartesian grid
p_etard=8.12E16
p_etaid=1.38E18
p1 = [(0.55+0.15*i)*p_etard for i in range(7)]
p2 = [(0.55+0.15*i)*p_etaid for i in range(7)]
collectionProblemData.declareIndexingSupport(parameters=("p_etard", "p_etaid"),
                                             training_set=np.meshgrid(p1, p2))


# Template dataset for the parametric computation

# Define dataset to the main input
# Defining the parametric case template
input_data = {"input_root_folder"      : osp.join(root_to_all, "template"),
              "input_main_file"        : "template.export",
              "input_instruction_file" : "template.comm",
              "input_resolution_data"  : constant_data,
              "input_result_path"      : "template_med_results",
              "input_result_type"      : "folder"}

solver_dataset = SolverDataset(ProblemData,
                               external_solver,
                               input_data)
collectionProblemData.setTemplateDataset(solver_dataset)

# ------------------------------------------------------------------
# DEFINE THE REDUCED CASE
# ------------------------------------------------------------------

# Template dataset of the reduced problem
# ---------------------------------------

input_data = {"input_root_folder"      : osp.join(root_to_all, "reduced"),
              "input_main_file"        : "template.export",
              "input_instruction_file" : "template.comm",
              "input_resolution_data"  : constant_data,
              "input_result_path"      : "template_med_results",
              "input_result_type"      : "folder"}
reduced_solver_dataset = ReducedSolverDataset(ReducedProblemData,
                                              external_solver,
                                              input_data)

# ReducedCase --> now ProblemData is used
# I suggest that it rather derives from CollectionProblemData
# -----------------------------------------------------------
my_reduced_case = ReducedCollectionProblemData(parent=collectionProblemData,
                                               template_dataset=reduced_solver_dataset)

# Main loop of the RB method
# --------------------------
stop_condition = False
is_first_iteration = True
#
while not stop_condition:

    # Proceed with next HF computation
    # --------------------------------
    problemData = collectionProblemData.solve(param_values=(p_etard, p_etaid))
    collectionProblemData.addProblemData(problemData)

    # Incremental POD to update the reduced basis
    # -------------------------------------------
    if is_first_iteration:
        
        # Standard code for standard POD
        # ------------------------------
        reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-4)
        
        # Note: couldn't these two steps be done in the previous one ?
        collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
        collectionProblemData.CompressSolutions("U")
    else:
        SP.incrementalEnrichment(reducedOrderBasisU,
                                 problemData.solutions["U"],
                                 1.e-4, 1.e-8)

    # Build operators for empirical quadrature
    # ----------------------------------------

    # NOTE: reducedOrderBasisU is a numpy array for now
    #       for now, we do not enrich yet with qualifying informations   
    nb_modes = reduced_basis.shape[0]
    if is_first_iteration:
        G = EQ.computeMatrix(problemData,
                             reducedOrderBasisU,
                             fieldHandler=MEDFieldHandler)
        y = EQ.computeRightHandSide(problemData,
                                    reducedOrderBasisU,
                                    fieldHandler=MEDFieldHandler)
    else:
        G = EQ.enrichMatrix(G,
                            problemData,
                            reducedOrderBasisU,
                            fieldHandler=MEDFieldHandler)
        y = EQ.enrichRightHandSide(y,
                                   problemData,
                                   reducedOrderBasisU,
                                   fieldHandler=MEDFieldHandler)  
    rho, NN0, ret = EQ.solve(G, y, volume, delta=1.e-5)

    # Turn empirical weight into a field
    # ----------------------------------
    gauss_field = EQ.buildReducedIntegrationField(rho, np_array_gauss_coor,
                                                  mesh, "PACE",
                                                  fieldHandler=MEDFieldHandler)
    # Incremental POD on the dual fields
    # ----------------------------------
    
    # Reuse the same code than for primal fields
    if is_first_iteration:
        reducedOrderBasisSigma = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData,
                                                                                      "sigma", 1.e-4)
        collectionProblemData.AddReducedOrderBasis("sigma", reducedOrderBasisSigma)
        collectionProblemData.CompressSolutions("sigma")
    else:
        SP.incrementalEnrichment(reducedOrderBasisSigma,
                                 problemData.solutions["sigma"],
                                 1.e-4, 1.e-8)

    # Add reduced integration scheme to solver dataset
    reduced_solver_dataset.set_reduced_integration_scheme(gauss_field)

    # Loop over the training set to find the next high-fidelity computation
    # ---------------------------------------------------------------------
    grid = np.dstack(collectionProblemData.indexingSupport.training_set).reshape((len(p1)*len(p2), 2))
    error = []
    for i, [etard, etaid] in enumerate(grid):

        # run the reduced order model
        reduced_problem_data = my_reduced_case.solve(param_values=(p_etard, p_etaid))

        # reconstruction of stress, gappy POD
        # code inspired from Safran's Mechanical.py
        # it would be good to put that code in a subfunction
        timeSequence = reduced_problem_data.GetOutputTimeSequence()

        # How to distinguish between (i)  values at the mask and
        #                            (ii) reduced coordinates of the data models ?
        # => They are distinct attributes of the ReducedSolution class, derived from Solution
        for t in timeSequence:
            ModesAtMask = reducedOrderBasisSigma[np.ix_(np.array(range(nb_modes)), np.nonzero(rho))]
            fieldAtMask = reduced_problem_data.solutions["sigma"].snapshotAtMask[t]
            reduced_problem_data.solutions["sigma"].compressedSnapshots[t] = GP.Fit(ModesAtMask, fieldAtMask)
        reduced_problem_data.solutions["sigma"].UncompressSnapshots(reducedOrderBasisSigma)

        # A posteriori error indicator
        # ----------------------------
        residual = external_solver.compute_equilibrium_residual(sigma)
        external_forces = external_solver.compute_external_loading(sigma)
        ap_err = 0.
        ap_ref = 0.
        for t in timeSequence:
            resid = residual.snapshots[t]
            force = external_forces.snapshots[t]

            # Take kinematic conditions into account in the residual
            Br = - matB @ resid
            from numpy import linalg
            multip = linalg.solve(matBBT, Br)
            corr_res = resid + matBT @ multip

            # On sort l'indicateur d'erreur
            ap_err = ap_err + 1./Nt * np.dot(corr_res, corr_res)
            ap_ref = ap_ref + 1./Nt * np.dot(   force,    force)
        
        error[i] = math.sqrt(ap_err)/math.sqrt(ap_ref)
    # TODO: réécrire avec des fonctions numpy
    i_max = error.index(max(error))
    p_etard, p_etaid = grid[i_max]
    stop_condition = error[i_max] < 1.e-4
