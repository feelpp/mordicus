//Readme pour le module NIRB:

************************************** 2D *******************************************************
peut lire les maillages .msh de gmsh ou FF++ et les maillages .vtu  


utilisation:
_avec base Greedy (nev à priori)
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOffline.py nev
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOnline.py

avec greedy posttraitement Rectification ajoutée
+ interpolation basictools possible si derniere version de basictools ajoutee dans le pythonpath
(NirbGreedyOnline_Basictools.py)


_avec base pod:
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbPodOffline.py
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbPodOnline.py

ns=nombre de snapshots (au début de chaque script)
mettre les snapshots au format vtu dans StationaryNSData/FineSnapshots/ sous le nom "snapshot"+str(i)+".vtu"
pour les maillages (fin et grossier) mettre sous le nom "mesh1.vtu" et "mesh2.vtu" (ou format legacy vtk pour l'interpolation dans freefem) dans StationaryNSData/FineMesh/ et StationaryNSData/CoarseMesh/

la solution grossiere peut etre lu avec basictools ou ff++
la placer dans le repertoire StationaryNSData/CoarseSolution
(la solution grossiere uHgrossier.vtk doit être au format ascii également si ff++)

Si greedy avec rectification: pour le moment l'interpolation des solutions est faite au préalable donc placer les vecteurs interpolés dans StationaryNSData/CoarseSnapshots en .vtu

Resultats dans StationaryNSData/ONLINE_RESU/ (erreur et approximation)


************************************** 3D *******************************************************
peut lire les maillages .msh de gmsh ou FF++ et les maillages .vtu

attention ns: nombre de snapshots, lecture direct de ns en comptant le nombre de fichiers dans le dossier 3DData/FineSnapshots/

utilisation:
_avec base Greedy (posttraitement rectification ajoutee)
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/3Dcase/NirbGreedyOffline_3D.py (on peut ajouter nev)
#attention nev<=ns nombre de snapshots

online: python mordicus/src/poc-1/examples/Modules/Sorbonne/3Dcase/NirbGreedyOnline_3D.py
#interpolation avec Basictools ou FF++

_avec base pod:
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/3Dcase/NirbPodOffline_3D.py
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/3Dcase/NirbPodOnline_3D.py

ns=nombre de snapshots (au début de chaque script)
mettre les snapshots au format vtu dans 3DData/FineSnapshots sous le nom "snapshot"+str(i)+".vtu"
pour les maillages (fin et grossier) mettre sous le nom "mesh1.vtu" et "mesh2.vtu" (format ascii .vtk pour l'interpolation dans freefem) dans 3DData/FineMesh et 3DData/CoarseMesh

la solution grossiere est uHgrossier0.vtu (et sinon uHgrossier.vtk doit être au format ascii également si FF++)
la solution grossiere peut etre lu avec basictools ou ff++
la placer dans le repertoire 3DData/CoarseSolution
(la solution grossiere uHgrossier.vtk doit être au format ascii également si ff++)

Si greedy avec rectification: placer les vecteurs grossiers dans 3DData/CoarseSnapshots en .vtu

Resultats dans 3DData/ONLINE_RESU/ (erreur et approximation)



