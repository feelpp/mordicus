import os
import os.path as osp
import numpy as np
import math
import shutil

from Mordicus.Modules.EDF.IO.Code_Aster_Solver import Code_Aster_Solver
from Mordicus.Modules.EDF.IO.MEDMeshReader import MEDMeshReader
from Mordicus.Modules.EDF.IO.MEDSolutionReader import MEDSolutionReader
from Mordicus.Modules.EDF.Containers.FieldHandlers.MEDFieldHandler import MEDFieldHandler


from Mordicus.Core.IO.SolverDataset import SolverDataset
from Mordicus.Core.Containers.FixedData.FixedDataBase import FixedDataBase
from Mordicus.Core.Containers.ResolutionData.ResolutionDataBase import ResolutionDataBase

from Mordicus.Core.Containers.CollectionProblemData import CollectionProblemData
from Mordicus.Core.Containers.ProblemData import ProblemData
from Mordicus.Core.Containers.Solution import Solution

from Mordicus.Core.DataCompressors.SnapshotPOD import ComputeReducedOrderBasisFromCollectionProblemData
from Mordicus.Core.OperatorCompressors import EmpiricalQuadrature as EQ
from Mordicus.Core.DataCompressors import SnapshotPOD as SP

from Mordicus.Modules.Safran.BasicAlgorithms import GappyPOD as GP
from Mordicus.Modules.EDF.DataCompressors.IncrementalSnapshotPOD import CompressData

# ------------------------------------------------------------------
# COMPUTATION OF CONSTANT DATA FOR THE HF AND REDUCED CASE
# ------------------------------------------------------------------

# Commande qui marche pour lancer un test:
# /home/A34370/dev/codeaster-prerequisites/v14_python3/tools/Code_aster_frontend-salomemeca/bin/as_run 
#     --vers=/home/A34370/dev/codeaster/install/std/share/aster --test sslv120a

# Ca ne marche pas avec --run, il faut faire avec --quick
# Ca marche aussi depuis un environnement vierge

# Pour que ca marche avec run, il faut ajouter les lignes suivantes au fichier export:
# P actions make_etude
# P version mordicus

# en ayant pris soin de definir la version dans ~/.astkrc/prefs :
# vers : mordicus:/home/A34370/dev/codeaster/install/std/share/aster

# On peut aussi definir dynamiquement cette nouvelle version dans le fichier export via son fichier de configuration
# F conf /home/A34370/dev/codeaster/install/std/share/aster/config.txt D  21

# Ca ne marche pas pour --run avec --vers en ligne de commande
root_to_all = osp.join(osp.dirname(osp.abspath(__file__)), "data")

# Definition of the solver -> NEW OBJECT
# --------------------------------------
def append_aster_dev_version(solver_dataset):
    """Function to append configuration file at the end of the export file"""
    input_root_folder = solver_dataset.input_data["input_root_folder"]
    input_main_file = solver_dataset.input_data["input_main_file"]
    solver_version = solver_dataset.solver.solver_cfg["solver_version"]
    try:
        with open(osp.join(input_root_folder, input_main_file), 'r') as f:
            if "config.txt" in f.readlines()[-1]:
                raise FileNotFoundError("Line already appended")
        with open(osp.join(input_root_folder, input_main_file), 'a') as f:
            f.write("F conf {solver_version}/share/aster/config.txt D 21".format(solver_version=solver_version))
    except FileNotFoundError:
        pass
        
call_script = """
{solver_install}/bin/as_run --run {input_root_folder}/{input_main_file}
"""

# Environment variables at the solver level
solver_cfg = {"solver_version" : "/home/A34370/dev/codeaster/install/std",
              "solver_install" : "/home/A34370/dev/codeaster-prerequisites/v14_python3/tools/Code_aster_frontend-salomemeca"
              }

external_solver = Code_Aster_Solver(solver_cfg=solver_cfg,
                                    solver_call_procedure_type="shell",
                                    python_preprocessing=append_aster_dev_version,
                                    call_script=call_script)

# Definition of the solver dataset -> NEW OBJECT
# ----------------------------------------------
input_data = {"input_root_folder" : osp.join(root_to_all, "step1"),
              "input_main_file"   : "arcad01a.export",
              "input_result_path" : "base_fixeddata",
              "input_result_type" : "folder"}

# Should InitialCondition, Loadings and ConstitutiveLaw derive from FixedData
solver_dataset = SolverDataset(FixedDataBase,
                               external_solver,
                               input_data)
fixed_data = solver_dataset.run()

# Read mesh -> REUSE EXISTING API
# -------------------------------

# Safran also offers static method MEDMeshReader.ReadMesh(meshFilename)
# The latter is chosen cause it retains the mesh path

# Pour avoir medcoupling avec python 3.5, on commence par l'installer depuis les paquets Debian
input_med_file = osp.join(root_to_all, "input_mesh.med")
reader_instance = MEDMeshReader(input_med_file)
mesh = reader_instance.ReadMesh()

#
# Compute Gauss point coordinates and volume
# ------------------------------------------

##Commented code to build approximation space anew, we are retrieving it from an example field
## 
##
#coor_elem_ref = [-1.e0, -1.e0, -1.e0, +1.e0, -1.e0, -1.e0, +1.e0, +1.e0, -1.e0, -1.e0, +1.e0, -1.e0, -1.e0, -1.e0, +1.e0, +1.e0, -1.e0, +1.e0, +1.e0, +1.e0, +1.e0, -1.e0, +1.e0, +1.e0, 0.e0, -1.e0, -1.e0, +1.e0,  0.e0, -1.e0, 0.e0, +1.e0, -1.e0, -1.e0,  0.e0, -1.e0, -1.e0, -1.e0,  0.e0, +1.e0, -1.e0,  0.e0, +1.e0, +1.e0,  0.e0, -1.e0, +1.e0,  0.e0, 0.e0, -1.e0, +1.e0, +1.e0,  0.e0, +1.e0, 0.e0, +1.e0, +1.e0, -1.e0,  0.e0, +1.e0]
#a =  [-0.774596669241483e0, 0.e0, 0.774596669241483e0]
#h =  [ 0.555555555555556e0, 0.888888888888889e0, 0.555555555555556e0]
#weight_gauss = []
#coor_gauss = []
#for ix in range(3):
#    for iy in range(3):
#        for iz in range(3):
#            weight_gauss.append(h[ix]*h[iy]*h[iz])
#            coor_gauss.append(a[ix])
#            coor_gauss.append(a[iy])
#            coor_gauss.append(a[iz])
#approx = ApproximationSpace("finite element", "P2-full",
#                            coor_elem_ref,
#                            coor_gauss,
#                            weight_gauss=weight_gauss)
#np_array_gauss_coor = mesh.gaussPointsCoordinates("PACE", approx)


reader_solution = MEDSolutionReader(osp.join(root_to_all, "sample", "sample_field.rmed"))
sample_field = reader_solution.readMEDField("sigma", 0.0)
sample_field_u = reader_solution.readMEDField("U", 0.0)
np_array_gauss_coor = mesh.gaussPointsCoordinates(sample_field)

volume = mesh.getVolume(sample_field)

# Get matrix B of kinematic conditions
# ------------------------------------
input_data = {"input_root_folder" : osp.join(root_to_all, "step2"),
              "input_main_file"   : "arcad01a.export",
              "input_result_path" : "matB.npy",
              "input_result_type" : "matrix"}
solver_dataset = SolverDataset(ResolutionDataBase,
                               external_solver,
                               input_data)
matB = solver_dataset.run()
matB = matB.GetInternalStorage()

# Debug MORDICUS/Aster
np.save("/home/A34370/tmp/comparison_Aster_Mordicus/Mordicus/matB.npy", matB)

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
#
# --- new syntax to be defined later on
# 
#solutionU = Solution(quantity=("U", "displacement", "m"),
#                       structure=(nbeOfComponentsPrimal, numberOfNodes),
#                       primality=True)
#
# --- old syntax
solutionU = Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality=True)

# The sigma field is not classical, there is not the same number of components per Gauss Points
# There is a necessity of providing a numpy array for the component structure
numberOfIntegrationPoints = np_array_gauss_coor.shape[1]
nbeOfComponentsDual = 6
#
# --- new syntax to be defined later on
#
#solutionSigma = Solution(quantity="sigma",
#                           structure=(vector_of_components, vector_of_points),
#                           primality=False)
#
# --- old syntax
solutionSigma = Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality=True)

# Define collectionProblemData
# ----------------------------

# CollectionProblemData: existing API
collectionProblemData = CollectionProblemData()

#
# --- new syntax
#problemData = PD.ProblemData(root_to_all,
#                             reference_support=mesh)
#problemData.AddSolution(solutionU)
#problemData.AddSolution(solutionSigma)
#collectionProblemData.declareReferenceProblemData(problemData)
#
# --- old syntax
collectionProblemData.SetFieldInstance("sigma", sample_field)
collectionProblemData.SetFieldInstance("U", sample_field_u)


# CollectionProblemData: extend the API, define parameters and indexation
collectionProblemData.defineQuantity("U", full_name="displacement", unit="meter")
collectionProblemData.defineQuantity("sigma", full_name="stress", unit="Pa")

collectionProblemData.defineVariabilityAxes(["p_etafd", "p_kdes"], 
                                            [float, float],
                                            quantities=[('viscosity', 'Pa.s'), ('viscosity', 'Pa.s')],
                                            descriptions=["recoverable creep coefficient",
                                                          "non recoverable creep coefficient"])

# Using np.meshgrid to define a cartesian grid
lst_etafd = [ 5.e7 , 5.e11]
lst_kdes  = [1.e-6 , 1.e-5]
p_etafd = lst_etafd[1]
p_kdes  = lst_kdes[0]
training_set = np.meshgrid(lst_etafd, lst_kdes, indexing='ij')
arr_etafd, arr_kdes = training_set
grid = np.column_stack((arr_etafd.flatten(), arr_kdes.flatten()))
collectionProblemData.defineIndexingSupport(("p_etafd", "p_kdes"),
                                            training_set=training_set)



# Template dataset for the parametric computation

# Define dataset to the main input
# Defining the parametric case template
input_data = {"input_root_folder"      : osp.join(root_to_all, "template"),
              "input_main_file"        : "template.export",
              "input_instruction_file" : "template.comm",
              "input_resolution_data"  : fixed_data,
              "input_result_path"      : "template.rmed",
              "input_result_type"      : "med_file"}

solver_dataset = SolverDataset(ProblemData,
                               external_solver,
                               input_data)
collectionProblemData.SetTemplateDataset(solver_dataset)

# ------------------------------------------------------------------
# DEFINE THE REDUCED CASE
# ------------------------------------------------------------------

# Template dataset of the reduced problem
# ---------------------------------------

input_data = {"input_root_folder"      : osp.join(root_to_all, "reduced"),
              "input_main_file"        : "reduced.export",
              "input_instruction_file" : "reduced.comm",
              "input_resolution_data"  : fixed_data,
              "input_result_path"      : "reduced.rmed",
              "input_result_type"      : "med_file"}
reduced_solver_dataset = SolverDataset(ProblemData,
                                       external_solver,
                                       input_data)

# ReducedCase --> now ProblemData is used
# I suggest that it rather derives from CollectionProblemData
# -----------------------------------------------------------
#
# --- new syntax
#my_reduced_case = ReducedCollectionProblemData(parent=collectionProblemData,
#                                               template_dataset=reduced_solver_dataset)
#
# --- old syntax
collectionProblemData.SetReducedTemplateDataset(reduced_solver_dataset)

# ------ Defining datasets for computing residuals
input_data = {"input_root_folder"      : osp.join(root_to_all, "compute_equilibrium_residual"),
              "input_main_file"        : "comp_eq_resid.export",
              "input_instruction_file" : "comp_eq_resid.comm",
              "input_resolution_data"  : fixed_data,
              "input_result_path"      : "comp_eq_resid.rmed",
              "input_result_type"      : "med_file"}
compute_residual_dataset = SolverDataset(ProblemData,
                                         external_solver,
                                         input_data)

# TODO remplace with a proper setter method
collectionProblemData.specificDatasets["compute_equilibrium_residual"] = compute_residual_dataset

fieldHandler = MEDFieldHandler()

# Main loop of the RB method
# --------------------------
stop_condition = False
is_first_iteration = True
#
while not stop_condition:

    # Proceed with next HF computation
    # --------------------------------
    problemData = collectionProblemData.solve(p_etafd=p_etafd, p_kdes=p_kdes)
    collectionProblemData.AddProblemData(problemData, p_etafd=p_etafd, p_kdes=p_kdes)

    # Incremental POD to update the reduced basis
    # -------------------------------------------
    if is_first_iteration:
        
        # Standard code for standard POD
        # ------------------------------
        reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-3)
        
        # Note: couldn't these two steps be done in the previous one ?
        collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
        collectionProblemData.CompressSolutions("U")
    else:
        nb_modes_old = reducedOrderBasisU.shape[0]
        reducedOrderBasisU = CompressData(collectionProblemData, "U", 1.e-4, snapshots=problemData.solutions["U"])
        newmodes = reducedOrderBasisU.shape[0] - nb_modes_old

    # Build operators for empirical quadrature
    # ----------------------------------------

    # NOTE: reducedOrderBasisU is a numpy array for now
    #       for now, we do not enrich yet with qualifying informations   
    nb_modes = reducedOrderBasisU.shape[0]
    if is_first_iteration:
        # Ok first version implemented
        print("Compute matrix and vector")

        G, y = EQ.computeMatrixAndVector(problemData,
                                         collectionProblemData,
                                         fieldHandler)
        print("End computing matrix and vector")
    else:
        # Ok first version implemented
        EQ.enrichMatrixAndVector(G, y,
                                 problemData,
                                 collectionProblemData,
                                 fieldHandler, newmodes)
    # Ok first version implemented
    print("Solving")

    rho = EQ.solve(G, y, volume, delta=5.e-6)
    np.save("/home/A34370/tmp/comparison_Aster_Mordicus/Mordicus/rho.npy", rho)

    print("rho = ", rho)
    print("End solving")


    # Turn empirical weight into a field
    # ----------------------------------
    fileNameWeights = osp.join(root_to_all, "empirical_weights.med")
    print("Writing field of empirical weights")
    reader_solution.WriteSparseFieldOfEmpiricalWeights(np_array_gauss_coor,
                                                       rho,
                                                       fileNameWeights,
                                                       sample_field)
    print("End writing field of empirical weights")
    
    # write POD basis
    fileNameModes = osp.join(root_to_all, "primal_modes.med")
    reader_solution.WriteReducedOrderBasis(reducedOrderBasisU, "U", sample_field_u, fileNameModes)


    # Incremental POD on the dual fields
    # ----------------------------------
    
    # Reuse the same code than for primal fields
    if is_first_iteration:
        print("Reduced basis for dual fields")

        reducedOrderBasisSigma = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData,
                                                                                      "sigma", 1.e-4)
        print("End reduced basis for dual fields")

        collectionProblemData.AddReducedOrderBasis("sigma", reducedOrderBasisSigma)
        print("End Adding reduced order basis")
        print("Start compressing solutions")

        collectionProblemData.CompressSolutions("sigma")
        print("End compressing solutions")

    else:
        reducedOrderBasisSigma = CompressData(collectionProblemData, "sigma", 1.e-5, snapshots=problemData.solutions["sigma"])


    # Add reduced integration scheme to solver dataset
    collectionProblemData.operatorCompressionData = fileNameWeights
    
    # use WriteSparseFieldOfEmpiricalWeights(self, np_coor_gauss, empirical_weights, fileName, fieldInstance) ?
    # Loop over the training set to find the next high-fidelity computation
    # ---------------------------------------------------------------------
    error = []
    for i, [etafd, kdes] in enumerate(grid):

        # run the reduced order model
        print("Start reduced resolution")

        reduced_problem_data, dataset_instance = collectionProblemData.solve_reduced(p_etafd=etafd, p_kdes=kdes)

        filePathRawReducedSolution = osp.join(dataset_instance.input_data["input_root_folder"], dataset_instance.input_data["input_result_path"])
        copyFilePathRawReducedSolution = osp.join(root_to_all, "tmp", "buffer_raw_reduced_solution_sigma.med")
        shutil.copyfile(filePathRawReducedSolution, copyFilePathRawReducedSolution)
        print("End reduced resolution")


        # reconstruction of stress, gappy POD
        # code inspired from Safran's Mechanical.py
        # it would be good to put that code in a subfunction
        timeSequence = reduced_problem_data.solutions["sigma"].GetTimeSequenceFromSnapshots()

        # How to distinguish between (i)  values at the mask and
        #                            (ii) reduced coordinates of the data models ?
        # => They are distinct attributes of the ReducedSolution class, derived from Solution
        # Getting modes at mask
        numberOfComponentsSigma = collectionProblemData.GetSolutionsNumberOfComponents("sigma")
        nb_modes_sigma = reducedOrderBasisSigma.shape[0]
        reshapedModes = reducedOrderBasisSigma.reshape((nb_modes_sigma,
                                                        collectionProblemData.GetSolutionsNumberOfNodes("sigma"),
                                                        numberOfComponentsSigma))
        ModesAtMaskNoFlatten = reshapedModes[np.ix_(np.array(range(nb_modes_sigma)),
                                                    np.nonzero(rho)[0],
                                                    np.array(range(numberOfComponentsSigma)))]
        ModesAtMask = ModesAtMaskNoFlatten.reshape((nb_modes_sigma, -1))

        for t in timeSequence:
            reshapedField = reduced_problem_data.solutions["sigma"].GetSnapshotAtTime(t).reshape((numberOfComponentsSigma,-1))
            fieldAtMaskNoFlatten = reshapedField[np.ix_(np.array(range(numberOfComponentsSigma)), 
                                                        np.nonzero(rho)[0])]
            fieldAtMask = fieldAtMaskNoFlatten.flatten()

            reduced_problem_data.solutions["sigma"].compressedSnapshots[t] = GP.Fit(ModesAtMask, fieldAtMask)

        # Equivalent du REST_REDUIT_COMPLET
        reduced_problem_data.solutions["sigma"].UncompressSnapshots(reducedOrderBasisSigma)
        #reduced_problem_data.solutions["U"].UncompressSnapshots(reducedOrderBasisU)

        
        # A ce stade, on a un resultat reconstruit qui est un objet Solution
        # Il faut reconstruire un résultat qu'on pourra donner a bouffer a Aster
        fileNameRecReducedSolution = osp.join(root_to_all, "tmp", "buffer_rec_reduced_solution_sigma.med")

        # sample_field est toujours le champ en contraintes
        reader_solution.WriteSolution(reduced_problem_data.solutions["sigma"],
                                      sample_field, "sigma",
                                      fileNameRecReducedSolution, name="SIG_REC")
        # sample_field est toujours le champ en contraintes
        reader_solution.WriteSolution(reduced_problem_data.solutions["U"],
                                      sample_field_u, "U",
                                      fileNameRecReducedSolution, name="U_REC", append=True)
        # Pour debug Mordicus/Aster
        shutil.copyfile(fileNameRecReducedSolution, "/home/A34370/tmp/comparison_Aster_Mordicus/Mordicus/reRedRec.med")
        # A posteriori error indicator
        # ----------------------------
        residualProblemData = collectionProblemData.compute_equilibrium_residual()
        ap_err = 0.
        ap_ref = 0.
        is_printed = False
        for t in timeSequence:
            resid = residualProblemData.GetSolution("r").snapshots[t]
            force = residualProblemData.GetSolution("Fext").snapshots[t]

            # Take kinematic conditions into account in the residual
            Br = - matB @ resid
            from numpy import linalg
            multip = linalg.solve(matBBT, Br)
            corr_res = resid + matBT @ multip

            # On sort l'indicateur d'erreur
            if t > 7.3e7:
                if not is_printed:
                    np.save("/home/A34370/tmp/comparison_Aster_Mordicus/Mordicus/resid.npy", resid)
                    np.save("/home/A34370/tmp/comparison_Aster_Mordicus/Mordicus/force.npy", force)

                ap_err = ap_err + 1./len(timeSequence) * np.dot(corr_res, corr_res)
                ap_ref = ap_ref + 1./len(timeSequence) * np.dot(   force,    force)
        
        error.append(math.sqrt(ap_err)/math.sqrt(ap_ref))
        print("error[", i, "] = ", error[i])
        # for debug Aster/Mordicus
        assert(False)
    # TODO: réécrire avec des fonctions numpy
    i_max = error.index(max(error))
    p_etafd, p_kdes= grid[i_max]
    stop_condition = error[i_max] < 1.e-4
    is_first_iteration = False
