#! /bin/bash

for i in `seq 1 20`;
do
    echo $i
    #python --version
    python3.6 NirbGreedyOffline_3D.py $i
    python3.6 NirbGreedyOnline_3D_Basictools.py $i
#    python3.6 NirbGreedyOnline_3D.py $i
    #python3.6 NirbPodOffline_3D.py $i
    #python3.6 NirbPodOnline_3D.py $i

done

