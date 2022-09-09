#!/bin/bash

dataFolder="~/feelppdb/nirb/heat"

removeOldDatas="rm -r ${dataFolder}"


Nsnap="2 4 8"
Rectification=0
biorthonormal=0

for n in $Nsnap;
do

Ns=$n

offline="python3 NIRBOffline.py ${Ns} ${Rectification}"
online="python3 NIRBOnline.py ${Rectification}"

${offline}
${online}

echo " ------------------------------------------ "  
echo "  Restarting program with Ns = : $Ns "  
echo " ------------------------------------------ "


done 
exit 


