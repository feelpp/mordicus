//Readme pour le module NIRB:

* 2D:

utilisation:
_avec base Greedy
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOffline.py
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOnline.py

avec greedy posttraitement Rectification ajoutée

_avec base pod:
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbPodOffline.py
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbPodOnline.py

ns=nombre de snapshots (au début de chaque script)
mettre les snapshots au format vtu dans StationaryNS sous le nom "snapshot"+str(i)+".vtu"
pour les maillages (fin et grossier) mettre sous le nom "mesh1.vtk" et "mesh2.vtk" (format ascii pour l'interpolation dans freefem)

la solution grossiere uHgrossier.vtk doit être au format ascii également



* 3D:

utilisation:
_avec base Greedy
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOffline_3D.py
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOnline_3D.py
or      python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbGreedyOnline_3D_Basictools.py
#interpolation avec Basictools et sinon avec FF++

avec greedy posttraitement Rectification ajoutée

_avec base pod:
offline: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbPodOffline_3D.py
online: python mordicus/src/poc-1/examples/Modules/Sorbonne/StationaryNS/NirbPodOnline_3D.py

ns=nombre de snapshots (au début de chaque script)
mettre les snapshots au format vtu dans StationaryNS sous le nom "snapshot"+str(i)+".vtu"
pour les maillages (fin et grossier) mettre sous le nom "mesh1.vtu" et "mesh2.vtu" (format ascii .vtk pour l'interpolation dans freefem)

la solution grossiere est uHgrossier0.vtu (et sinon uHgrossier.vtk doit être au format ascii également si FF++)



