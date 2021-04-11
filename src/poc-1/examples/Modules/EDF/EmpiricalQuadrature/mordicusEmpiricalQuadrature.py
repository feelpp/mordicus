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
from Mordicus.Core.DataCompressors import SnapshotPOD as SP

from Mordicus.Modules.EDF.OperatorCompressors import EmpiricalQuadrature as EQ
from Mordicus.Modules.EDF.DataCompressors.IncrementalSnapshotPOD import CompressData
from Mordicus.Modules.EDF.BasicAlgorithms.GappyPOD import GappyPOD_EQ

# root folder to all study subfolders where solver input and output files will be put

root_to_all = osp.join(osp.dirname(osp.abspath(__file__)), "data")

# ------------------------------------------------------------------
# I. DEFINITION OF THE SOLVER
# ------------------------------------------------------------------
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
solver_cfg = {"solver_version" : "/home/A34370/dev/codeaster/install/std",
              "solver_install" : "/home/A34370/dev/codeaster-prerequisites/v14_python3/tools/Code_aster_frontend-salomemeca"
              }
external_solver = Code_Aster_Solver(solver_cfg=solver_cfg,
                                    solver_call_procedure_type="shell",
                                    python_preprocessing=append_aster_dev_version,
                                    call_script=call_script)

# ------------------------------------------------------------------
# II. DEFINITION OF FIXED DATA = REUSABLE INPUT DATA FOR SOME COMPUTATION
# ------------------------------------------------------------------
input_data = {"input_root_folder" : osp.join(root_to_all, "step1"),
              "input_main_file"   : "arcad01a.export",
              "input_result_path" : "base_fixeddata",
              "input_result_type" : "folder"}

solver_dataset = SolverDataset(FixedDataBase,
                               external_solver,
                               input_data)
fixed_data = solver_dataset.run()



# ------------------------------------------------------------------
# III. READ MESH
# ------------------------------------------------------------------
input_med_file = osp.join(root_to_all, "input_mesh.med")
reader_instance = MEDMeshReader(input_med_file)
mesh = reader_instance.ReadMesh()

# ------------------------------------------------------------------
# IV. READ SOLUTION STRUCTURE
# ------------------------------------------------------------------
reader_solution = MEDSolutionReader(osp.join(root_to_all, "sample", "sample_field.rmed"), 0.0)
fieldHandler = MEDFieldHandler()

solution_structure_sigma = reader_solution.ReadSolutionStructure("sigma",
                                                                 "gauss",
                                                                 components=["SIXX", "SIYY", "SIZZ", "SIXY", "SIXZ", "SIYZ"],
                                                                 dimsRelativeToMax=[0])

solution_structure_u = reader_solution.ReadSolutionStructure("U",
                                                             "node")

np_array_gauss_coor = fieldHandler.gaussPointsCoordinates(solution_structure_sigma)
volume = fieldHandler.getVolume(solution_structure_sigma)

# ------------------------------------------------------------------
# V. READ FULL SCALE RESOLUTION DATA: HERE MATRIX B OF KINEMATIC CONDITIONS
# ------------------------------------------------------------------
fileNameNumbering = osp.join(root_to_all, "numbering.med")
reader_solution.WriteNumbering(fileNameNumbering, solution_structure_u, "U", nameInFile="number")

print("fixed_data.GetInternalStorage() = ", fixed_data.GetInternalStorage())
input_data = {"input_root_folder"   : osp.join(root_to_all, "step2"),
              "input_mordicus_data" : {"mordicus_fixed_data": fixed_data.GetInternalStorage(),
                                       "mordicus_numbering" : fileNameNumbering},
              "input_main_file"     : "arcad01a.export",
              "input_result_path"   : "matB.npy",
              "input_result_type"   : "matrix"}
solver_dataset = SolverDataset(ResolutionDataBase,
                               external_solver,
                               input_data)
matB = solver_dataset.run()
matB = matB.GetInternalStorage()

# Computation needed for the error estimate
# -----------------------------------------
matBT = matB.copy()
matBT = np.transpose(matBT)
matBBT = matB @ matBT

# ------------------------------------------------------------------
# VI.DEFINE THE STRUCTURE OF THE CASE
# ------------------------------------------------------------------

# The displacement field is defined on 3D and 1D elements
numberOfNodes         = solution_structure_u.GetNumberOfNodes()
nbeOfComponentsPrimal = 3
solutionU = Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality=True)

# The sigma field is defined only on 3D elements
nbeOfComponentsDual = 6
numberOfIntegrationPoints = solution_structure_sigma.GetNumberOfNodes()
solutionSigma = Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality=True)

# Define collectionProblemData and solution structures
collectionProblemData = CollectionProblemData()
collectionProblemData.SetSolutionStructure("sigma", solution_structure_sigma)
collectionProblemData.SetSolutionStructure("U", solution_structure_u)


# Define physical quantities corresponding to solutions
collectionProblemData.defineQuantity("U", full_name="displacement", unit="meter")
collectionProblemData.defineQuantity("sigma", full_name="stress", unit="Pa")

# Define the caracteristics of varying parameters
collectionProblemData.defineVariabilityAxes(["p_etafd", "p_kdes"], 
                                            [float, float],
                                            quantities=[('viscosity', 'Pa.s'), ('viscosity', 'Pa.s')],
                                            descriptions=["recoverable creep coefficient",
                                                          "non recoverable creep coefficient"])

# Define the support of varying parameters
arr_etafd = np.array([ 5.e9 , 5.e11])
arr_kdes  = np.array([5.e-5 , 1.e-5])
collectionProblemData.defineVariabilitySupport(["p_etafd", "p_kdes"],
                                               [arr_etafd, arr_kdes])

p_etafd = arr_etafd[0]
p_kdes  = arr_kdes[0]

# ------------------------------------------------------------------
# VII. DEFINE TEMPLATE FOR HF PARAMETRIC COMPUTATION
# ------------------------------------------------------------------
input_data = {"input_root_folder"      : osp.join(root_to_all, "template"),
              "input_main_file"        : "template.export",
              "input_instruction_file" : "template.comm",
              "input_mordicus_data"    : {"mordicus_fixed_data": fixed_data.GetInternalStorage()},
              "input_result_path"      : "template.rmed",
              "input_result_type"      : "med_file"}
solver_dataset = SolverDataset(ProblemData,
                               external_solver,
                               input_data)
collectionProblemData.SetTemplateDataset(solver_dataset)

# ------------------------------------------------------------------
# VII. DEFINE TEMPLATE FOR REDUCED PARAMETRIC COMPUTATION
# ------------------------------------------------------------------
fileNameModes = osp.join(root_to_all, "primal_modes.med")
fileNameWeights = osp.join(root_to_all, "empirical_weights.med")

input_data = {"input_root_folder"      : osp.join(root_to_all, "reduced"),
              "input_main_file"        : "reduced.export",
              "input_instruction_file" : "reduced.comm",
              "input_mordicus_data"    : {"mordicus_fixed_data"        : fixed_data.GetInternalStorage(),
                                          "mordicus_primal_modes"      : fileNameModes,
                                          "mordicus_empirical_weights" : fileNameWeights},
              "input_result_path"      : "reduced.rmed",
              "input_result_type"      : "med_file"}
reduced_solver_dataset = SolverDataset(ProblemData,
                                       external_solver,
                                       input_data)
collectionProblemData.SetReducedTemplateDataset(reduced_solver_dataset)

# ------------------------------------------------------------------
# VIII. DEFINE DATASET FOR SPECIFIC OPERATIONS
# ------------------------------------------------------------------
fileNameRecReducedSolution = osp.join(root_to_all, "tmp", "buffer_rec_reduced_solution_sigma.med")

input_data = {"input_root_folder"      : osp.join(root_to_all, "compute_equilibrium_residual"),
              "input_main_file"        : "comp_eq_resid.export",
              "input_instruction_file" : "comp_eq_resid.comm",
              "input_mordicus_data"    : {"mordicus_fixed_data"                     : fixed_data.GetInternalStorage(),
                                          "mordicus_reduced_solution_reconstructed" : fileNameRecReducedSolution},
              "input_result_path"      : "comp_eq_resid.rmed",
              "input_result_type"      : "med_file"}
compute_residual_dataset = SolverDataset(ProblemData,
                                         external_solver,
                                         input_data)

collectionProblemData.specificDatasets["computeAPosterioriError"] = compute_residual_dataset


# ------------------------------------------------------------------
# XI. MAIN LOOP OF THE REDUCED BASIS METHOD
# ------------------------------------------------------------------
stop_condition = False
is_first_iteration = True
#
while not stop_condition:

    # 1. Proceed with next HF computation
    # -----------------------------------
    problemData = collectionProblemData.solve(p_etafd=p_etafd, p_kdes=p_kdes,
                                              extract=("U", "sigma"),
                                              primalities={"U": True, "sigma": False},
                                              solutionReaderType=MEDSolutionReader)

    collectionProblemData.AddProblemData(problemData, p_etafd=p_etafd, p_kdes=p_kdes)

    # 2. Compression of data : incremental POD to update the reduced basis
    # --------------------------------------------------------------------
    if is_first_iteration:
        reducedOrderBasisU = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData, "U", 1.e-3)
        
        # Note: couldn't these two steps be done in the previous one ?
        collectionProblemData.AddReducedOrderBasis("U", reducedOrderBasisU)
        collectionProblemData.CompressSolutions("U")
    else:
        nb_modes_old = reducedOrderBasisU.shape[0]
        reducedOrderBasisU = CompressData(collectionProblemData, "U", 1.e-4, snapshots=problemData.solutions["U"])
        newmodes = reducedOrderBasisU.shape[0] - nb_modes_old

    # write POD basis
    reader_solution.WriteReducedOrderBasis(fileNameModes, solution_structure_u, reducedOrderBasisU, "U")

    # 3. Compression of operators
    # ---------------------------
    
    # a : build dictionary and signal of interest
    # -------------------------------------------
    nb_modes = reducedOrderBasisU.shape[0]
    if is_first_iteration:
        G, y = EQ.computeMatrixAndVector(fieldHandler,
                                         problemData,
                                         collectionProblemData)

    else:
        EQ.enrichMatrixAndVector(G, y,
                                 problemData,
                                 collectionProblemData,
                                 fieldHandler, newmodes)

    # b : solve sparse representation problem
    # ---------------------------------------
    rho = EQ.solve(G, y, volume, delta=5.e-6)

    # c : Turn empirical weight into a field
    # --------------------------------------
    reader_solution.WriteSparseFieldOfEmpiricalWeights(fileNameWeights,
                                                       solution_structure_sigma,
                                                       np_array_gauss_coor,
                                                       rho)

    # 4. POD on dual quantity
    # -----------------------
    
    # Reuse the same code than for primal fields
    if is_first_iteration:
        reducedOrderBasisSigma = SP.ComputeReducedOrderBasisFromCollectionProblemData(collectionProblemData,
                                                                                      "sigma", 1.e-4)
        collectionProblemData.AddReducedOrderBasis("sigma", reducedOrderBasisSigma)
        collectionProblemData.CompressSolutions("sigma")

    else:
        reducedOrderBasisSigma = CompressData(collectionProblemData, "sigma", 1.e-5, snapshots=problemData.solutions["sigma"])

    # Add reduced integration scheme to solver dataset
    collectionProblemData.operatorCompressionData = fileNameWeights
    
    # 5. Loop over the training set to find the next high-fidelity computation
    # ------------------------------------------------------------------------
    error = []
    for i, [etafd, kdes] in enumerate(collectionProblemData.generateVariabilitySupport()):

        # a. Run the reduce order model
        # -----------------------------
        reduced_problem_data, result_file_path = collectionProblemData.solve_reduced(p_etafd=etafd, p_kdes=kdes,
                                                                                     extract=("U", "sigma"),
                                                                                     primalities={"U": True, "sigma": False},
                                                                                     solutionReaderType=MEDSolutionReader)

        # b. Gappy POD on stresses
        # ------------------------
        
        # --- Compute reduced coordinates
        GappyPOD_EQ(collectionProblemData, rho, reduced_problem_data)
        
        # --- Reconstruct fields from these reduced coordinates
        reduced_problem_data.solutions["sigma"].UncompressSnapshots(reducedOrderBasisSigma)
        #reduced_problem_data.solutions["U"].UncompressSnapshots(reducedOrderBasisU)

        # c. Write the solution
        # ---------------------
        reader_solution = MEDSolutionReader(result_file_path, 0.0)

        reader_solution.WriteSolution(fileNameRecReducedSolution,
                                      solution_structure_sigma,
                                      reduced_problem_data.solutions["sigma"],
                                      "sigma", nameInFile="SIG_REC")

        reader_solution.WriteSolution(fileNameRecReducedSolution,
                                      solution_structure_u,
                                      reduced_problem_data.solutions["U"],
                                      "U", nameInFile="U_REC", append=True)

        # d. A posteriori error indicator
        # -------------------------------
        residualProblemData = collectionProblemData.computeAPosterioriError(extract=("r", "Fext"),
                                                                            solutionStructures={"r": collectionProblemData.solutionStructures["U"],
                                                                                                "Fext": collectionProblemData.solutionStructures["U"]},
                                                                            primalities={"r": False, "Fext": False},
                                                                            solutionReaderType=MEDSolutionReader)

        ap_err = 0.
        ap_ref = 0.
        timeSequence = reduced_problem_data.solutions["sigma"].GetTimeSequenceFromSnapshots()
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
                ap_err = ap_err + 1./len(timeSequence) * np.dot(corr_res, corr_res)
                ap_ref = ap_ref + 1./len(timeSequence) * np.dot(   force,    force)
        
        error.append(math.sqrt(ap_err)/math.sqrt(ap_ref))
        print("error[", i, "] = ", error[i])
        # for debug Aster/Mordicus
        assert(False)
    
    i_max = error.index(max(error))
    p_etafd, p_kdes = collectionProblemData.generateVariabilitySupport()[i_max]
    stop_condition = error[i_max] < 1.e-4
    is_first_iteration = False
