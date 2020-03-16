from Mordicus.Modules.CT.IO import MeshReader as MR
from Mordicus.Modules.CT.IO import VTKSolutionReader as VSR
from Mordicus.Core.Containers import ProblemData as PD
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Core.Containers import Solution as S
from Mordicus.Core.DataCompressors import SnapshotPOD
from Mordicus.Core.OperatorCompressors import Regression
from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
from Mordicus.Modules.CT.IO import numpyToVTKWriter as NTV
import numpy as np
from pathlib import Path
import os
import math

import vtk

initFolder = os.getcwd()
currentFolder = str(Path(__file__).parents[0])
os.chdir(currentFolder)
    
class ROM(object):

    def __init__(self, parameters, outputTimeSequence, solutionName, mesh):

        assert isinstance(parameters, list)    
        assert isinstance(outputTimeSequence, list)    
        self.parameters = parameters
        self.outputTimeSequence = outputTimeSequence
        self.solutionName = solutionName

        self.mesh = mesh
        self.numberOfNodes = self.mesh.GetNumberOfNodes()
        self.nbeOfComponents = 1
        self.primality = True

        self.collectionProblemData = CPD.CollectionProblemData()
        self.onlineProblemData = PD.ProblemData("Online")
    


    def Dataset(self, Ind):
    
        for i in range(len(self.parameters)):
            folder = "Computation" + str(Ind[i] + 1) + "/"
    
            solution = S.Solution(
                solutionName=self.solutionName,
                nbeOfComponents=self.nbeOfComponents,
                numberOfNodes=self.numberOfNodes,
                primality=self.primality,
            )
    
            problemData = PD.ProblemData(folder)
            problemData.AddSolution(solution)
    
    
            count=0
            for t in self.outputTimeSequence:
                print('\ntime   ', t)
                #solutionFileName = folder + "fields_"+str(count)+".vtu"
                solutionFileName = folder + "fields_"+str(count)+".npy"
                solutionReader = VSR.VTKSolutionReader(solutionFileName)
    
                snapshot = solutionReader.npReadSnapshot(
                    solution.GetSolutionName(), t, self.nbeOfComponents
                )
                solution.AddSnapshot(snapshot, t)
                problemData.AddParameter(np.array(self.parameters[i]), t)
                print('Data      ' , solutionFileName)
                print('Parameters' , problemData.GetParameters().get(t))
                count +=1
    
            self.collectionProblemData.AddProblemData(problemData)
    
        print("\nSolutions have been read\n")



##################################################
# OFFLINE
##################################################

    def POD(self):
    
        reducedOrderBasis = SnapshotPOD.ComputeReducedOrderBasisFromCollectionProblemData(
            self.collectionProblemData, self.solutionName, 1.0e-4
        )
    
        self.collectionProblemData.AddReducedOrderBasis(self.solutionName, reducedOrderBasis)
        print("Reduced order bases have been constructed using SnapshotPOD")
    

    def CompressFit(self):
    
        self.collectionProblemData.CompressSolutions(self.solutionName)
        print("The solution has been compressed")
        #for _, problemData in self.collectionProblemData.GetProblemDatas().items():
        #    print('CompressedSnapshots ', problemData.solutions[self.solutionName].GetCompressedSnapshots().get(0.0))
   
    
        from sklearn.gaussian_process.kernels import WhiteKernel, RBF
        from sklearn.gaussian_process import GaussianProcessRegressor
    
        kernel = 1.0 * RBF(length_scale=100.0, length_scale_bounds=(1e-2, 1e3)) + WhiteKernel(
            noise_level=1, noise_level_bounds=(1e-10, 1e1)
        )
        gpr = GaussianProcessRegressor(kernel=kernel, alpha=0.0)
    
        Regression.CompressOperator(
            self.collectionProblemData, self.solutionName, gpr
        )
    
        self.collectionProblemData.SaveState("mordicusState")
    

    def WritePOD(self, VTKBase):
    
        numpyToVTK = NTV.VTKWriter(VTKBase)
        reducedOrderBasis = self.collectionProblemData.GetReducedOrderBasis(self.solutionName)
        numpyToVTK.numpyToVTKPODWrite(self.solutionName, reducedOrderBasis)
    
    
##################################################
# ONLINE
##################################################

    def Predict(self, onlinetimeseq, onlineparameter):
    
        solution = S.Solution(
            solutionName=self.solutionName,
            nbeOfComponents=self.nbeOfComponents,
            numberOfNodes=self.numberOfNodes,
            primality=self.primality,
        )
        self.onlineProblemData.AddSolution(solution)


        OnlineTimeSequence = np.array(onlinetimeseq, dtype=float)
    
        for t in OnlineTimeSequence:
            self.onlineProblemData.AddParameter(np.array(onlineparameter), t)
    

        reducedOrderBasis = self.collectionProblemData.reducedOrderBases[self.solutionName]
        operatorCompressionData = self.collectionProblemData.GetOperatorCompressionData()
        compressedSnapshots = Regression.ComputeOnline(
            self.onlineProblemData, operatorCompressionData
        )
        PW.WritePXDMF(self.mesh, compressedSnapshots, reducedOrderBasis, self.solutionName)
        print("The compressed solution has been written in PXDMF Format")

        solution.SetCompressedSnapshots(compressedSnapshots)
        solution.UncompressSnapshots(reducedOrderBasis)
    
    
    def WriteRec(self, VTKBase):

        ###write Rec. Solution
        numpyToVTK = NTV.VTKWriter(VTKBase)
        numpyToVTK.numpyToVTKSanpWrite(self.solutionName, self.onlineProblemData.solutions[self.solutionName].GetSnapshotsList())
    
        os.chdir(initFolder)

    def SnapIter(self):
        
        snaps = self.collectionProblemData.SnapshotsIterator(self.solutionName)
        snapshots = []
        for s in snaps:
            snapshots.append(s)

        snapshots = np.array(snapshots)

        return snapshots

    def GetSnapOnline(self):
        
        snaps = self.onlineProblemData.solutions[self.solutionName].GetSnapshotsList()
        snapshots = np.array(snaps)

        return snapshots

    def SimpVol(self, vertices):
        distance = np.transpose([vertices[0] - vi for vi in vertices[1:]])
        return np.abs(
            np.linalg.det(distance) / math.factorial(vertices.shape[1]))

    def mkVtkIdList(self, it):
      vil = vtk.vtkIdList()
      for i in it:
        vil.InsertNextId(int(i))
      return vil
    
    def CreateErrVTK(self, arrayVertices, arrayTriangles, labelsScalars, arrayScalars):
      # arrayVertices : list of triples [[x1,y1,z2], [x2,y2,z2], ... ,[xn,yn,zn]] of vertex coordinates
      # arrayVertexNormals : list of triples [[nx1,ny1,nz2], [nx2,ny2,nz2], ... ] of vertex normals
      # arrayTriangles : list of triples of 0-based indices defining triangles
      # labelsScalars : list of strings to label the individual scalars data sets
      # arrayScalars : an array of n rows for n vertices and m colums for m inidividual scalar sets
    
      # create the building blocks of polydata including data attributes.
      mesh    = vtk.vtkPolyData()
      points  = vtk.vtkPoints()
      #normals = vtk.vtkFloatArray()
      polys   = vtk.vtkCellArray()
      
      # load the array data into the respective VTK data structures
      for i in range(len(arrayVertices)):
        points.InsertPoint(i, arrayVertices[i])
    
    
      for i in range(len(arrayTriangles)):
        polys.InsertNextCell(self.mkVtkIdList(arrayTriangles[i]))
      
      #for i in range(len(arrayVertexNormals)):
      #  normals.InsertTuple3(i, arrayVertexNormals[i][0], arrayVertexNormals[i][1], arrayVertexNormals[i][2])
    
      # put together the mesh object
      mesh.SetPoints(points)
      mesh.SetPolys(polys)
      #if(len(arrayVertexNormals) == len(arrayVertices)):
      #  mesh.GetPointData().SetNormals(normals)
    
      
      # Add scalars
      scalars = []
      for j in range(len(labelsScalars)):
        scalars.append(vtk.vtkFloatArray())
        
        #for i in range(len(arrayVertices)):
        for i in range(len(arrayScalars)):
          scalars[j].InsertTuple1(i,arrayScalars[i][j])
        
        scalars[j].SetName(labelsScalars[j])
        #mesh.GetPointData().AddArray(scalars[j])
        mesh.GetCellData().AddArray(scalars[j])
    
      out_fname = 'error.vtp'
      writer = vtk.vtkXMLPolyDataWriter()
      writer.SetFileName(out_fname)
      writer.SetInputData(mesh)
      writer.Write()
      print('error.vtp written')


    def CreateErrTetraVTK(self, arrayVertices, arrayTriangles, labelsScalars, arrayScalars):
      IDS = np.split(np.arange(0, len(arrayTriangles)*4), len(arrayTriangles))

      vtk_pts = vtk.vtkPoints()

      for ind in range(len(arrayTriangles)):
        tetraInd = arrayTriangles[ind]
        tetraPnt = arrayVertices[tetraInd]

        # Create the grid points
        vtk_pts.InsertNextPoint(tetraPnt[0][0], tetraPnt[0][1], tetraPnt[0][2])
        vtk_pts.InsertNextPoint(tetraPnt[1][0], tetraPnt[1][1], tetraPnt[1][2])
        vtk_pts.InsertNextPoint(tetraPnt[2][0], tetraPnt[2][1], tetraPnt[2][2])
        vtk_pts.InsertNextPoint(tetraPnt[3][0], tetraPnt[3][1], tetraPnt[3][2])

      # Create the unstructured grid
      grid = vtk.vtkUnstructuredGrid()
      grid.SetPoints(vtk_pts)
      
      # Allocate space for the cells in the grid

      tetra = vtk.vtkTetra()
      cellArray = vtk.vtkCellArray()
      # Loop through all cells
      for i in range(len(arrayTriangles)):
          cell_ids = IDS[i]
          tetra.GetPointIds().SetId(0, cell_ids[0])
          tetra.GetPointIds().SetId(1, cell_ids[1])
          tetra.GetPointIds().SetId(2, cell_ids[2])
          tetra.GetPointIds().SetId(3, cell_ids[3])

          cellArray.InsertNextCell(tetra)

      grid.SetCells(vtk.VTK_TETRA, cellArray)
      #print (grid.GetNumberOfCells())


      scalars = []
      for j in range(len(labelsScalars)):
        scalars.append(vtk.vtkFloatArray())
      
        #for i in range(len(arrayVertices)):
        for i in range(len(arrayScalars)):
          scalars[j].InsertTuple1(i,arrayScalars[i][j])
      
        scalars[j].SetName(labelsScalars[j])
        grid.GetCellData().AddArray(scalars[j])


      out_fname = 'error.vtu'
      writer = vtk.vtkXMLUnstructuredGridWriter()
      writer.SetFileName(out_fname)
      writer.SetInputData(grid)
      writer.Write()
      print('error.vtu written')





#############################################################
#############################################################

#initial data
print('Read VTK base file')
VTKBaseMesh = MR.ReadVTKBase("meshBase.vtu")
print('Read mesh')
mesh = MR.ReadMesh("meshBase.vtu")

#Parameters = [[0.3, 0.0], [0.3, 15.0], [0.8, 0.0], [0.8, 15.0]]   ###two parameters
Parameters = [[0.3, 0.0, 0], [0.3, 15.0, 0], [0.8, 0.0, 0], [0.8, 15.0, 0], [0.3, 0.0, 3], [0.3, 15.0, 3], [0.8, 0.0, 3], [0.8, 15.0, 3]] ###three parameters
DataInd = list(range(len(Parameters)))
OutputTimeSequence = [0.]
SolutionName = "Mach"
print('SolutionName ', SolutionName)


if __name__ == "__main__":

    #Offline phase for the starting parameters 
    rom = ROM(Parameters, OutputTimeSequence, SolutionName, mesh)
    rom.Dataset(DataInd)
    rom.POD()
    rom.CompressFit()
    rom.WritePOD(VTKBaseMesh)

    ##Online phase for one parameter
    #OnlineTimeSeq = np.arange(0, 1, 10)
    #OnlineParameter = [0.3, 8.0]
    #rom.Predict(OnlineTimeSeq, OnlineParameter)
    #rom.WriteRec(VTKBaseMesh)

    #initial set of snapshots for the calucaltion of the loo error
    snaps = rom.SnapIter()
    numberOfDOFs = snaps.shape[1]
    numberOfSnapshots = snaps.shape[0]


    #Leave One Out method.
    error = np.zeros(len(Parameters))
    for j in DataInd:
        UsedInd = DataInd[:]
        UsedInd.remove(j)
        NewPar = np.array(Parameters)[UsedInd].tolist()
        romLO = ROM(NewPar, OutputTimeSequence, SolutionName, mesh)
        romLO.Dataset(UsedInd)
        romLO.POD()
        romLO.CompressFit()
    
        OnlineTimeSeq = np.arange(0, 1, 10)
        OnlineParameter = Parameters[j]
        print('Leave One Out OnlineParameter ', OnlineParameter)
        romLO.Predict(OnlineTimeSeq, OnlineParameter)
    
        error[j] = np.linalg.norm(snaps[j] - romLO.GetSnapOnline())
    
    print('Leave One Out error ', error)


    #calcualtion of next points in the parameter space. Initial simplex has to be convex.
    points = np.array(Parameters)
    error = error

    from scipy.spatial import Delaunay
    triangles = Delaunay(points)
    
    ind=0
    errorSimplex = np.zeros((len(triangles.simplices)))
    for simp in triangles.simplices:
        errorSimplex[ind] = np.sum(error[simp]) * rom.SimpVol(points[simp])
        ind=ind+1
    print('simplices error ', errorSimplex)
    
    k=1  ###number of points
    newBaryPoint = []
    for ind in np.argsort(errorSimplex)[-k:]:
        trianglesPnt = points[triangles.simplices[ind]]
        print('worst simplex points\n', trianglesPnt)
        trianglesErr = error[triangles.simplices[ind]]
        print('worst simplex error', np.sum(trianglesErr) * rom.SimpVol(trianglesPnt))
    
        newBaryPoint.append(
            np.average(trianglesPnt, axis=0, weights=trianglesErr))

    print('New error weighted barycentric point of the worst simplex', newBaryPoint)
    

    #Error representation in VTK
    if np.size(points,1) ==2:
        points3dN = np.zeros((np.size(points, 0),np.size(points, 1)+1))
        points3dN[:,:-1] = points

        #Normalization for plotting
        points3dN[:,0] = points3dN[:,0] / max(points3dN[:,0])
        points3dN[:,1] = points3dN[:,1] / max(points3dN[:,1])
    
        nameScalar = ['error']
        err = errorSimplex.reshape((len(errorSimplex), 1))
        rom.CreateErrVTK(points3dN, triangles.simplices, nameScalar, err)
    elif np.size(points,1) ==3:
        pointsN = np.zeros((np.size(points, 0),np.size(points, 1)))
        #Normalization for plotting
        pointsN[:,0] = points[:,0] / max(points[:,0])
        pointsN[:,1] = points[:,1] / max(points[:,1])
        pointsN[:,2] = points[:,2] / max(points[:,2])

        nameScalar = ['error']
        err = errorSimplex.reshape((len(errorSimplex), 1))
        rom.CreateErrTetraVTK(pointsN, triangles.simplices, nameScalar, err)




