import petsc4py 
from petsc4py import PETSc
import os 
from mpi4py import MPI 



def LoadPetscArrayBin(filename):
    """ Load a PETSc array from filename writing in binary format """
    outputfile = os.path.join(filename)
    viewer = PETSc.Viewer().createBinary(outputfile, 'r')
    PetscAray = PETSc.Mat().load(viewer)
    return PetscAray

def SavePetscArrayBin(filename, PetscAray):
    """ Save a PETSc array on filename in binary format """
    outputfile = os.path.join(filename)
    
    viewer = PETSc.Viewer().createBinary(outputfile, 'w')
    viewer(PetscAray)


def SavePetscArrayASCII(filename, PetscAray):
    """ Save a PETSc array on filename in ASCII format """

    outputfile = os.path.join(filename)

    myviewer = PETSc.Viewer().createASCII(
    outputfile, format=PETSc.Viewer.Format.ASCII_COMMON,
    comm= PETSc.COMM_WORLD)
    PetscAray.view(myviewer)

def WriteVecAppend(filename, array):
    """ Write an array or list in filename with append mode 
            the vector value will be writen horizontally 
    """
    with open(filename, 'a+') as file:
        file.write(' '.join(str(i) for i in list(array))+"\n")
