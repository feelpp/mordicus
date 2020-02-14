# -*- coding: utf-8 -*-
import numpy as np
import vtk

from vtk.util import numpy_support
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
from mpi4py import MPI
from pathlib import Path
import os


primalSolutionComponents = {1:[""], 2:["1", "2"], 3:["1", "2", "3"]}


def WritePOD(VTKBase, solutionName, reducedOrderBasis):
    """
    Functional API
    
    Reads a snapshots from the Z-set solution file "solutionFileName" (.ut), at time "time" and of primality "primality", from the HF computation
            
    Parameters
    ----------
    solutionFileName : str
        Z-set solution file
    fieldName : str
        name of the solution from which the snapshot is read
    time : float
        time at which the snapshot is read
    primality : bool
        primality of the solution from which the snapshot is read
                    
    Returns
    -------
    np.ndarray
        of size (numberOfDofs,)
    """
    writer = VTKWriter(VTKBase = VTKBase)
    return writer.numpyToVTKWrite(solutionName, reducedOrderBasis)



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



    def numpyToVTKPODWrite(self, solutionName, reducedOrderBasis):

        nmpyPODModes_array = reducedOrderBasis
        #print('\nPOD modes (numberOfModes, numberOfDOFs) ', nmpyPODModes_array.shape)
        
        p = self.VTKBase.GetPointData()
        for ind in range(0,nmpyPODModes_array.shape[0]):
            nmpyPODMode_array = nmpyPODModes_array[ind,:]

            VTK_data = numpy_support.numpy_to_vtk(num_array=nmpyPODMode_array.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
            VTK_data.SetName("POD_mode "+ str(solutionName) + ' ' + str(ind))
            name = VTK_data.GetName()
            size = VTK_data.GetSize()
            
            p.AddArray(VTK_data)
        
        out_fname = 'PODmodes.vtu'
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(out_fname)
        writer.SetInputData(self.VTKBase)
        writer.SetDataModeToAscii()
        writer.Write()
        print('\nfile ', out_fname, ' written\n' )

    def numpyToVTKSanpWrite(self, solutionName, SnapshotsList):

        numpySnap_array = SnapshotsList[0]
        
        p = self.VTKBase.GetPointData()

        VTK_data = numpy_support.numpy_to_vtk(num_array=numpySnap_array.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data.SetName("Rec Sol "+ str(solutionName))
        name = VTK_data.GetName()
        size = VTK_data.GetSize()
        
        p.AddArray(VTK_data)
        
        out_fname = 'RecSol.vtu'
        writer = vtk.vtkXMLUnstructuredGridWriter()
        writer.SetFileName(out_fname)
        writer.SetInputData(self.VTKBase)
        writer.SetDataModeToAscii()
        writer.Write()
        print('\nfile ', out_fname, ' written\n' )

    

