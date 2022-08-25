import petsc4py 
from petsc4py import PETSc
import os 
from mpi4py import MPI 


def SavePetscArrayBin(filename, PetscAray):

    outputfile = os.path.join(filename)
    
    viewer = PETSc.Viewer().createBinary(outputfile, 'w')
    viewer(PetscAray)


def SavePetscArrayASCII(filename, PetscAray):

    outputfile = os.path.join(filename)

    myviewer = PETSc.Viewer().createASCII(
    outputfile, format=PETSc.Viewer.Format.ASCII_COMMON,
    comm= PETSc.COMM_WORLD)
    PetscAray.view(myviewer)
