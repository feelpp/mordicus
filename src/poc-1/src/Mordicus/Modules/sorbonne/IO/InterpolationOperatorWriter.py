# -*- coding: utf-8 -*-
import numpy as np
import vtk
import os
import os.path as osp
from vtk.util import numpy_support
from mpi4py import MPI
from pathlib import Path
import os
from Mordicus.Core.IO import StateIO as SIO
from Mordicus.Modules.Safran.FE import FETools as FT
from BasicTools.FE import FETools as FT2
from BasicTools.FE.Fields.FEField import FEField
from BasicTools.Containers import Filters
from BasicTools.Containers.UnstructuredMeshFieldOperations import GetFieldTransferOp
import subprocess
from scipy.sparse import coo_matrix
from Mordicus.Modules.sorbonne.IO import MeshReader as MR

#option=ff/basictools
def InterpolationOperator(dataFolder,mesh1,mesh2,dimension,option=None):
    #os.chdir('../')
    #print(os.getcwd())
    externalFolder=osp.join(dataFolder,'../','External')
    print(externalFolder)
    if option=="ff":
        # call of freefem (output: InterpolI.txt)
        print("interpolation with FreeFem++")

        scriptFreeFemInterpolation=osp.join(externalFolder,'FF_Interpolation_Mat_3D.edp')
        try:
            FNULL = open(os.devnull, 'w')
            ret = subprocess.run(["FreeFem++", scriptFreeFemInterpolation,
                                  "-m1"   , mesh1,
                                  "-m2"   , mesh2,
                                  "-outputDir", dataFolder+"/Matrices"
            ],
                                 stdout=FNULL,
                                 stderr=subprocess.PIPE)
            ret.check_returncode()
        except subprocess.CalledProcessError:
            retstr = "Error when calling Freefem++, interpolation script\n" + "    Returns error:\n" + str(ret.stderr)
            raise OSError(ret.returncode, retstr)

        file=open(dataFolder+"/Matrices/interpolI.txt","r")
        file.readline()
        file.readline()
        t=file.readline().split()
        #t=t.split()
        n=int(t[0])
        m=int(t[1])
        print("n ",n," m ",m)
        nnz=int(t[2])
        row,col,data=np.zeros(nnz),np.zeros(nnz),np.zeros(nnz)
        cpt=0
        for line in file:
            t=line.split()
            row[cpt]=int(t[0])
            col[cpt]=int(t[1])
            data[cpt]=float(t[2])
            cpt=cpt+1
        operator=coo_matrix((data, (row, col)), shape=(n, m))
        
        #SIO.SaveState(dataFolder+"/Matrices/operator",operator)
        
    elif option=="basictools":
        
        #coarse mesh
        
        meshReader2=MR.MeshReader(mesh2,dimension)
        mesh2 = meshReader2.ReadMesh()
        mesh2.GetInternalStorage().nodes = mesh2.GetInternalStorage().nodes
        inputmesh=FT.ConvertMeshToUnstructuredMesh(mesh2)
        #space, numberings,_, _ = FT2.PrepareFEComputation(inputmesh)
        inputFEField =FEField(name="field",mesh=inputmesh)#,space=space,numbering=numberings[0])
        #inputFEField.SetDataFromPointRepresentation(mesh2, fillvalue=0.)
        #Fine mesh
        meshReader = MR.MeshReader(mesh1,dimension)
        mesh = meshReader.ReadMesh()
        mesh.GetInternalStorage().nodes = mesh.GetInternalStorage().nodes
        outmesh=FT.ConvertMeshToUnstructuredMesh(mesh)
        outnodes = outmesh.nodes
        methods = ["Interp/Nearest","Nearest/Nearest","Interp/Clamp","Interp/Extrap"]
        method = methods[1]

        #interpolation
        operator, status = GetFieldTransferOp(inputFEField,outnodes,method = method,verbose=True) #interpolation!

        #SIO.SaveState(dataFolder+"/Matrices/operator",operator)
        
    else:
        print("non recognized option for interpolation")
    return operator
