# -*- coding: utf-8 -*-
import numpy as np
import vtk

from vtk.util import numpy_support
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
import os
from BasicTools.Containers import Filters



primalSolutionComponents = {1:[""], 2:["1", "2"], 3:["1", "2", "3"]}


def WriteVTK(VTKBase, solutionName, reducedOrderBasis):
    """
    Functional API
    
    Write a solution from numpy array to vtk format
            
    Parameters
    ----------
    solutionFieldName : str
        name of the solution 
    time : float
        time at which the snapshot is read
    
    Returns
    -------
    vtk file
        of size (numberOfDofs,)
    """
    writer = VTKWriter(VTKBase = VTKBase)
    return writer.numpyToVTKWrite(solutionName, reducedOrderBasis,filename)



class VTKWriter(SolutionReaderBase):
    """
    Class containing writers for VTK files

    Attributes
    ----------
    VTKBase : vtu data structure
        name of the VTK data structure (.vtu)
    """

    def __init__(self, VTKBase):
        """
        Parameters
        ----------
        VTKBase : vtu data structure
        """
        super(VTKWriter, self).__init__()

        self.VTKBase = VTKBase



    def numpyToVTKPODWrite(self, solutionName, reducedOrderBasis,filename):
        """
        write the reduced basis in vtk format from numpy array
        ----------
        VTKBase : vtu data structure
        """
        nmpyPODModes_array = reducedOrderBasis
        #print('\nPOD modes (numberOfModes, numberOfDOFs) ', nmpyPODModes_array.shape)
        
        p = self.VTKBase.GetPointData()
        #for ind in range(0,nmpyPODModes_array.shape[0]):
        size=np.shape(nmpyPODModes_array)
        print(size[0])
        #print(size[1])
        n=size[0]/2
        nmpyPODMode_array = nmpyPODModes_array[:].reshape(int(n),2)
        print(nmpyPODMode_array)
        #cas 2D
        
        #VTK_data = numpy_support.numpy_to_vtk(num_array=nmpyPODMode_array.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data = numpy_support.numpy_to_vtk(num_array=nmpyPODMode_array, deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data.SetName("POD_mode"+ str(solutionName))
        name = VTK_data.GetName()
        print(name)
        size = VTK_data.GetSize()
        print("size array", size)
        p.AddArray(VTK_data)
        
        out_fname = filename #'PODmodes.vtu'
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(out_fname)
        writer.SetInputData(self.VTKBase)
        writer.SetDataModeToAscii()
        writer.Write()
        print('\nfile ', out_fname, ' written\n' )


    def numpyToVTKmatWrite(self, solutionName, reducedOrderBasis,filename):
        p = self.VTKBase.GetPointData()
        n=reducedOrderBasis.shape[0]
        m=reducedOrderBasis.shape[1]
        print("n",n,"m",m)
        nmpyPODModes_array = np.zeros((reducedOrderBasis.shape[0],reducedOrderBasis.shape[1]))
        for i in range(reducedOrderBasis.shape[0]):
            for j in range(reducedOrderBasis.shape[1]):
                nmpyPODModes_array[i,j]=reducedOrderBasis[i,j]
            nmpyPODMode_array = nmpyPODModes_array[i,:].reshape(int(n/2),2)
            VTK_data = numpy_support.numpy_to_vtk(num_array=nmpyPODMode_array, deep=True, array_type=vtk.VTK_FLOAT)
            VTK_data.SetName("mat_mode"+ str(i))
            name = VTK_data.GetName()
            print(name)
            size = VTK_data.GetSize()
            print("size array", size)
            p.AddArray(VTK_data)
        
        out_fname = filename #'PODmodes.vtu'
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(out_fname)
        writer.SetInputData(self.VTKBase)
        writer.SetDataModeToAscii()
        writer.Write()
        print('\nfile ', out_fname, ' written\n' )


        
    def numpyToVTKSanpWrite(self, SnapshotsList, FieldName="U", solutionName="Approximation.vtu"):
        """
        write the solution in vtk format from numpy array
        ----------
        VTKBase : vtu data structure
        """
        numpySnap_array = SnapshotsList#[0]
        #print("shape vtkfile", np.shape(numpySnap_array))
        
        p = self.VTKBase.GetPointData()
        #print("P",p)
        #print("vtkbase ", self.VTKBase)
        #VTK_data = numpy_support.numpy_to_vtk(num_array=numpySnap_array.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data = numpy_support.numpy_to_vtk(num_array=numpySnap_array, deep=True, array_type=vtk.VTK_FLOAT)
        size = VTK_data.GetSize()
        #print("size array", size)
        VTK_data.SetName(FieldName)
        name = VTK_data.GetName()
        p.AddArray(VTK_data)
        
        out_fname = solutionName #'RecSol.vtu'

        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(out_fname)
        writer.SetInputData(self.VTKBase)
        writer.SetDataModeToAscii()
        writer.Write()
        print('\nfile ', out_fname, ' written\n' )


    def numpyToVTKSanpWriteFromGMSH(self, SnapshotsList,FieldName="U", solutionName="Approximation.vtu"): #GMSH + NUMPY_ARRAY
        """
        write the solution in vtk format from numpy array and gmsh mesh
        ----------
        VTKBase : vtu data structure
        """
        
        numpySnap_array = SnapshotsList#[0]
        #print("shape vtkfile", np.shape(numpySnap_array))
        
        p=self.VTKBase.nodes
        numberOfNodes=np.shape(p)[0]
        
        vtkPts = vtk.vtkPoints()
        #for i in range(numberOfNodes):
        #    vtkPts.InsertNextPoint(p[i])
        vtkPts.SetData(numpy_support.numpy_to_vtk(p, deep=True))
        VTKBase = vtk.vtkUnstructuredGrid()
        VTKBase.SetPoints(vtkPts)#pts
        #print(VTKBase)
        
        #VTK_data = numpy_support.numpy_to_vtk(num_array=numpySnap_array.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data = numpy_support.numpy_to_vtk(num_array=numpySnap_array, deep=True, array_type=vtk.VTK_FLOAT)
        
        size = VTK_data.GetSize()
        #print("size array", size)
        VTK_data.SetName(FieldName)
        name = VTK_data.GetName()
        VTKBase.GetPointData().AddArray(VTK_data)

        triangulation = vtk.vtkDelaunay2D()
        triangulation.SetInputData(VTKBase)
        triangulation.Update()

        appendFilter = vtk.vtkAppendFilter()
        appendFilter.AddInputData(triangulation.GetOutput())
        appendFilter.Update()

        VTKBase.ShallowCopy(appendFilter.GetOutput())

        out_fname = solutionName #'RecSol.vtu'
        #print("solutionName")
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(out_fname)
        writer.SetInputData(VTKBase)
        writer.SetDataModeToAscii()
        writer.Write()
        print('\nfile ', out_fname, ' written\n' )
