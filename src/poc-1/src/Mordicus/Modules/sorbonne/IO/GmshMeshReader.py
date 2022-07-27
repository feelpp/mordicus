# -*- coding: utf-8 -*-
import numpy as np
from Mordicus.Core.IO.MeshReaderBase import MeshReaderBase
from mpi4py import MPI
from pathlib import Path
import os
#import meshio
import argparse


def ReadMesh(meshFileName):
    """
    Functional API
    
    Reads the mesh defined the Gmsh mesh file "meshFileName" (.msh)
            
    Parameters
    ----------
    meshFileName : str
        Gmsh mesh file 
                    
    Returns
    -------
    BasicToolsUnstructuredMesh
        mesh of the HF computation
    """
    reader = GmshMeshReader(meshFileName=meshFileName)
    return reader.ReadMesh()

def ReadGMSHBase(meshFileName):
    """
    Functional API
    
    Reads the file "meshFileName" VTK (.vtu)
            
    Parameters
    ----------
    meshFileName : str
        VTK mesh and fields file 
                    
    Returns
    -------
    VTK data structure (UnstructuredMesh)
        mesh and fields of the HF computation
    """
    reader = GmshMeshReader(meshFileName=meshFileName)
    return reader.ReadGmshBase()

class GmshMeshReader(MeshReaderBase):
    """
    Class containing a reader for Z-set mesh file

    Attributes
    ----------
    meshFileName : str
        name of the GMSH mesh file (.msh)
    """

    def __init__(self, meshFileName):
        """
        Parameters
        ----------
        meshFileName : str, optional
        """
        super(GmshMeshReader, self).__init__()

        assert isinstance(meshFileName, str)
            

        folder = str(Path(meshFileName).parents[0])
        suffix = str(Path(meshFileName).suffix) #.msh
        stem = str(Path(meshFileName).stem) #mesh
        
        
        if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover 
            self.meshFileName = folder + os.sep + stem + "-pmeshes" + os.sep + stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
        else:
            self.meshFileName = meshFileName

    def ReadMesh(self):
        """
        Read the HF GMSH mesh
                    
        Returns
        -------
        BasicToolsUnstructuredMesh
            mesh of the HF computation
        """
        #from GmshReader import ReadGmsh as Read
        from BasicTools.IO.GmshReader import ReadGmsh as Read
        data=Read(self.meshFileName)
       
        #print("data",data)
        from Mordicus.Modules.Safran.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM

        mesh = BTUM.BasicToolsUnstructuredMesh(data)

        return mesh
    def ReadGmshBase(self):
        
        
        suffix = str(Path(self.meshFileName).suffix)
        assert suffix == ".msh", "! Filename error !"
      
        from BasicTools.IO.GmshReader import ReadGmsh as Read
        GMSHBase=Read(self.meshFileName)

        return GMSHBase

def CheckAndConvertMeshFFtoGMSH(meshFileName,meshFileNameGMSH,dimension):
     """
    Functional API
    
    Convert the mesh from FreeFem++ to Gmsh mesh format "meshFileName" (.msh)
            
    Parameters
    ----------
    meshFileName : str
        Gmsh or FF++ mesh file 
                    
    Returns
    -------
    GMSH mesh
        mesh of the HF computation
    """

     print("meshfilename: ",meshFileName)
     meshFile=open(meshFileName,"r")
     firstline=meshFile.readline()
     firstlineGMSH="MeshFormat"

     if firstline[1:-1] == firstlineGMSH[:]: #if already in GMSH
         print("GMSH format")
         #os.rename(meshFileName, meshFileNameGMSH)
         return 1
     else: #if FreeFem++ format, convert to GMSH format
         print("Convert FF++ format to GMSH...")
     
         ConvertFFtoGMSH(meshFileName,meshFileNameGMSH,dimension)
         print("Converted!")
         return 0

def ConvertFFtoGMSH(meshFileName,meshFileNameGMSH,dimension):
    assert dimension==2 or dimension==3, "Error dimension must be 2 or 3"
    # Read file and store data
    infile = open(meshFileName, 'r') 
    outfile = open(meshFileNameGMSH, 'w') 
    Lines = infile.readlines()

    # first line is "NNodes NTri Nseg"
    data = Lines[0].strip('\n').split(" ")
    nnodes = int(data[0])
    nelem = []
    nelem_tot = 0
    for d in data[1:len(data)]:
        nelem.append(int(d))
        nelem_tot += int(d)
    print("Nnodes = " + str(nnodes) + "\nNelem  = "+str(nelem_tot))

    # Header
    outfile.write("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$Nodes\n");
    # Points
    cpt = 1 #line counter
    outfile.write(str(nnodes)+"\n");
    for i in range(nnodes):
        if(dimension==2):
            outfile.write(str(i+1)+ " " + Lines[cpt][:-2]+" "+str(0)+"\n");
        else:
            outfile.write(str(i+1)+ " " + Lines[cpt]);
        cpt += 1
    outfile.write("$EndNodes\n");
    # Element
    outfile.write("$Elements\n");
    outfile.write(str(nelem_tot)+"\n");
    for i in range(nelem_tot):
    #Loop on all element, without knowing what type they are
        elem = Lines[cpt].strip('\n').split(" ")
        if(len(elem)==3):
      # Segment
            outfile.write(str(i+1)+ " " ) # new element
            outfile.write("1 2 " + str(elem[2])+ " 0 " + str(elem[0]) +" "+str(elem[1])+"\n")
        elif(len(elem)==4):
            #Triangle
            outfile.write(str(i+1)+ " " ) # new element
            outfile.write("2 2 " + str(elem[3])+ " 0 " + str(elem[0]) +" "+str(elem[1])+" "+str(elem[2])+"\n")
        else:
            #Do not know
            print("unrecognized format! ")
        cpt += 1
    outfile.write("$EndElements\n");
    # close everything
    infile.close()
    outfile.close()
