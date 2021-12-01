//Readme NIRB Sorbonne module:

// General script


In NIRBOffline.py:

modify:
	. the names of the folders

	"""
	# 3D Case (3D example)
	externalFolder=osp.join(currentFolder,'3Dcase/External') #FreeFem scripts
	OfflineResuFolder=osp.join(currentFolder,'3Dcase/3DData/FineSnapshots/') #folder for offline resu
	FineDataFolder=osp.join(currentFolder,'3Dcase/3DData/FineSnapshots/') #folder for fine snapshots
	CoarseDataFolder=osp.join(currentFolder,'3Dcase/3DData/CoarseSnapshots/') #folder for coarse snapshots
	FineMeshFolder=osp.join(currentFolder,'3Dcase/3DData/FineMesh/') #folder for fine mesh (needed with Freefem snapshots)
	CoarseMeshFolder=osp.join(currentFolder,'3Dcase/3DData/CoarseMesh/') #folder for coarse mesh (needed with Freefem)

	"""
	# 2D case (2D example)
	externalFolder=osp.join(currentFolder,'StationaryNS/External') #FreeFem scripts
	OfflineResuFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineSnapshots/') #folder for offline resu
	FineDataFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineSnapshots/') #folder for fine snapshots
	CoarseDataFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/CoarseSnapshots/') #folder for coarse snapshots
	FineMeshFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/FineMesh/') #folder for fine mesh (needed with Freefem snapshots)
	CoarseMeshFolder=osp.join(currentFolder,'StationaryNS/StationaryNSData/CoarseMesh/') #folder for coarse mesh (needed with Freefem)


      . the parameters


      dimension=2 #dimension spatial domain
      nbeOfComponentsPrimal = 2 # number of primal components 
      FieldName="Velocity" #Snapshots fieldname
      Format= "FreeFem" # FreeFem or VTK
      Method="Greedy" #POD or Greedy
      Rectification=1 #1 with Rectification post-process (Coarse Snapshots required) or 0 without




************************************** 2D *******************************************************
can read .msh meshes from gmsh or FreeFem++ and .vtu meshes


use:
_with Greedy algorithm (nev a priori/ *****  RIC needs to be added ****** )

offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/NIRBOffline.py nev
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/NIRBOnline.py

with greedy posttreatement Rectification added (if Rectification=1)
+ interpolation basictools (basictools must be in the pythonpath!)

_possible with pod basis:
Method="POD" #POD or Greedy (nev with RIC)



_ Indications:

FineMesh and CoarseMesh correspond to fine and coarse meshes
Meshes and snapshots computed beforehand with FreeFem in mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/script_donnees_init.edp or other solver + output in VTK
(test freefem, converted in GMSH, and read with Basictools)
ns=number of snapshots (directly calculated from the number of vtu files)
Test 2D FreeFem++ case, with only one  .txt with all the snapshots (ns directly calculated, ok with P1 ******  case P2 + several fields, given in parameter needs to be added *********)

Snapshots FreeFEm++: the snapshots are converted in vtk, saved and read  (FFSolutionReader in  sorbonne module). Then the solutions are read in a forloop and transformed in nparrays

interpolations of the coarse snapshots (used for post-treatment or online part) : operator calculated with the sorbonne module  InterpolationOperatorWriter (InterpolationOperator function can use FreeFem or Basictools). In 2D, griddata can also be used directly

_ To launch a new case :
  #### OFFLINE ####
  Fine mesh in ".msh" in the folder "FineMeshFolder" (not necessary with .vtu)
  If rectification posttreatment, coarse mesh with ".msh" in "CoarseMeshFolder"  
  Fine snapshots in "FineDataFolder" (one file .txt for FF++)
  If rectification,coarse snapshots in the folder " "CoarseDataFolder"
  -> output of script offline in OfflineResuFolder: collectionProblemData.pkl (+ Meshes in GMSH format if FreeFem++ in the folders of the meshes)
  
   #### ONLINE ####
  Fine mesh in ".msh" in the folder "FineMeshFolder" (not necessary with .vtu)
  If rectification posttreatment, coarse mesh with ".msh" in "CoarseMeshFolder"  
  If computing errors (H1, L2), fine solution in "FineDataFolder" (one file .txt for FF++)
  Coarse solution in the folder " "CoarseDataFolder"
  -> output of script online in OnlineResuFolder: .vtu +errors (options)



