//Readme pour le module NIRB:

************************************** 2D *******************************************************
peut lire les maillages .msh de gmsh ou FF++ et les maillages format .vtu  


utilisation:
_avec base Greedy (nev à priori)
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOffline.py nev
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOnline.py

avec greedy posttraitement Rectification ajoutée
+ interpolation basictools (basictools ajoutee dans le pythonpath)

_possible avec avec base pod:
dans mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOffline.py: au lieu de "reducedOrderBasisU=GD.Greedy(snapshots,l2ScalarProducMatrix,h1ScalarProducMatrix,nev) # greedy algorithm" utiliser la snapshotPOD

_ Indications:
FineMesh et CoarseMesh correspondent aux maillages fins et maillages grossiers
Maillage et snapshots calculés au préalable avec FreeFem dans mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/script_donnees_init.edp
(ici au format freefem, convertit en GMSH, et lit avec Basictools;)
ns=nombre de snapshots (au début de chaque script)
ici cas FreeFem++, avec un fichier .txt contenant tous les snapshots (ns est directement calculé, ok avec du P1)
Ensuite les snapshots sont convertis au format vtk et sauvegardés puis lus (FFSolutionReader dans module sorbonne).
les solutions sont ensuite lues dans une boucle et transformées en nparrays.
Interpolations des snapshots grossiers (utilisés pour le post-traitement de la rectification avec un operator calculé à l'aide du module sorbonne InterpolationOperatorWriter (fonction InterpolationOperator peut utiliser FreeFem ou Basictools), module griddata possible en 2D avec python directement.

_ Pour lancer avec un nouveau cas test 2D avec FreeFem:
  #### OFFLINE ####
  mettre le maillage fin sous la forme "mesh1.msh" dans  mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/StationaryNSData) ou modifier ligne 76 (script offline)
  mettre le maillage grossier sous la forme "mesh2.msh" dans StationaryNSData ou modifier ligne 77 (script offline)
  mettre les snapshots fins dans le fichier "snapshots.txt dans StationaryNSData (ou modifier l. 81)
  mettre les snapshots grossiers dans le fichier "coarsesnapshots.txt" (ou modifier l.82)
  -> sortie script offline: collectionProblemData.pkl (+ Maillages au format GMSH )
   #### ONLINE ####
  
_ Pour lancer avec un nouveau cas test 2D avec le format VTK (et par exemple la PODSnapshots)
   #### OFFLINE ####
  mettre le maillage fin et les snapshots fins dans StationaryNSData (format .vtu)
  modifier nom des fichiers snapshots sous la forme snapshots_i.vtu (i=0....ns) ou modifier l. 76 (FineSnapshotFiles=sorted(glob.glob(dataFolder+"/snapshots_*")))
  modifier FieldName= "u" l. 74 
  modifier le nombre de champs à lire nbeOfComponentsPrimal = 2 l.89
  -> sortie script offline: Resultats dans collectionProblemData.pkl 
   #### ONLINE ####
    mettre les maillages fin/grossier et les solutions fine/grossiere dans StationaryNSData (format .vtu)
    modifier nom solution grossier soluH_0.vtu ou modifier l. 61
    modifier nom solution fine snapshot_9.vtu l.52
    modifier FieldName= "u" l. 34 
    modifier le nombre de champs à lire nbeOfComponentsPrimal = 2 l.58
 -> sortie erreur H1/L2 (+ possible: approximation au format .vtu)

************************************** 3D *******************************************************
peut lire les maillages .msh de gmsh ou FF++ et les maillages .vtu

attention ns: nombre de snapshots, lecture direct de ns en comptant le nombre de fichiers dans le dossier 3DData/FineSnapshots/

utilisation:
_avec base Greedy (posttraitement rectification ajoutee)
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/3Dcase/NirbGreedyOffline_3D.py (on peut ajouter nev)
#attention nev<=ns nombre de snapshots

online: python mordicus/src/poc-1/examples/Modules/Sorbonne/3Dcase/NirbGreedyOnline_3D.py
#interpolation avec Basictools ou FF++

ns=nombre de snapshots (au début de chaque script)
mettre les snapshots au format vtu dans 3DData/FineSnapshots sous le nom "snapshot"+str(i)+".vtu"
pour les maillages (fin et grossier) mettre sous le nom "mesh1.vtu" et "mesh2.vtu" (format ascii .vtk pour l'interpolation dans freefem) dans 3DData/FineMesh et 3DData/CoarseMesh

la solution grossiere est uHgrossier0.vtu (et sinon uHgrossier.vtk doit être au format ascii également si FF++)
la solution grossiere peut etre lu avec basictools ou ff++
la placer dans le repertoire 3DData/CoarseSolution
(la solution grossiere uHgrossier.vtk doit être au format ascii également si ff++)

Si greedy avec rectification: placer les vecteurs grossiers dans 3DData/CoarseSnapshots en .vtu

Resultats dans 3DData/ONLINE_RESU/ (erreur et approximation)



