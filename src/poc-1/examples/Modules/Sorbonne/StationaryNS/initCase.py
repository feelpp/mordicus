import os
import os.path as osp

import subprocess


"""
Create data (mesh1,mesh2,snapshots,uH) for Sorbonne     usecase
"""


def initproblem(dataFolder):
        
    """ 
    ----------------------------
                  generate snapshots
    ----------------------------
    """ 
    
    ## Directories
    currentFolder=os.getcwd()
    
    #outputsFolder=osp.join(currentFolder,'Outputs')
    
    ## Script Files - Initiate data
    externalFolder=osp.join(currentFolder,'External')
    
    scriptFreeFem=osp.join(externalFolder,'script_donnees_init.edp')
            
    try:
        FNULL = open(os.devnull, 'w')
        ret = subprocess.run(["FreeFem++", scriptFreeFem, "-outputDir", dataFolder, ">sortie"],
        stdout=FNULL,stderr=subprocess.PIPE)
        ret.check_returncode()
                
                
    except subprocess.CalledProcessError:
        retstr = "Error when calling Freefem++\n" + "    Returns error:\n" + str(ret.stderr)
        raise OSError(ret.returncode, retstr)
    
    print("Files generated in "+dataFolder+ " : snapshots.txt, soluH.txt, mesh1.msh, mesh2.msh")
    return "OK"

def basisFileToArray(tmpbaseFile,nev):
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
    # Loop over temporary VTK files
    array_list = []
    for i in range(nev):
        reader = vtk.vtkXMLUnstructuredGridReader()
        reader.SetFileName(tmpbaseFile + str(i) + ".vtu")
        reader.Update()
        fdata = reader.GetOutput().GetPointData()
        u1_vtk_array = fdata.GetArray("u")
        u1_np_array = vtk_to_numpy(u1_vtk_array)
        array_list.append(u1_np_array)
    return u1_np_array



def VTKReadToNp(tmpbaseFile,nev_i):
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
    from BasicTools.IO.VtuReader import LoadVtuWithVTK
    from vtk.numpy_interface import dataset_adapter as dsa
    data = LoadVtuWithVTK(tmpbaseFile + str(nev_i) + ".vtu")
    npArray = dsa.WrapDataObject(data).GetPointData().GetArray("u")
    return npArray



if __name__ == "__main__":
    dataFolder=osp.join('StationaryNSData')

    print(dataFolder)  # pragma: no cover
