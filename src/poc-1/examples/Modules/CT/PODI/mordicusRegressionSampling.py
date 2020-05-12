from Mordicus.Modules.CT.IO import MeshReader as MR
from Mordicus.Modules.CT.ROM import ROM as RM
import numpy as np


#initial data
print('Read VTK base file')
VTKBaseMesh = MR.ReadVTKBase("meshBase.vtu")
print('Read mesh')
mesh = MR.ReadMesh("meshBase.vtu")

#ParametersValues = [[0.3, 0.0], [0.3, 15.0], [0.8, 0.0], [0.8, 15.0]]   ###two parameters
ParametersDefinition = (['mu1', 'mu2', 'mu3'], 
                        [float, float, int],
                        [('Quantity 1', 'unit1'), ('Quantity 2', 'unit2'), None],
                        ['description 1', 'description 2', 'description 3'])
ParametersValues = [[0.3, 0.0, 0], [0.3, 15.0, 0], [0.8, 0.0, 0], [0.8, 15.0, 0], [0.3, 0.0, 3], [0.3, 15.0, 3], [0.8, 0.0, 3], [0.8, 15.0, 3]] ###three parameters
DataInd = list(range(len(ParametersValues)))
OutputTimeSequence = [0.]
SolutionName = "Mach"
print('SolutionName ', SolutionName)


if __name__ == "__main__":

    #Offline phase for the starting parameters 
    rom = RM.ROM(ParametersDefinition, ParametersValues, OutputTimeSequence, SolutionName, mesh)
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
    error = np.zeros(len(ParametersValues))
    for j in DataInd:
        UsedInd = DataInd[:]
        UsedInd.remove(j)
        NewPar = np.array(ParametersValues)[UsedInd].tolist()
        romLO = ROM(NewPar, OutputTimeSequence, SolutionName, mesh)
        romLO.Dataset(UsedInd)
        romLO.POD()
        romLO.CompressFit()
    
        OnlineTimeSeq = np.arange(0, 1, 10)
        OnlineParameter = ParametersValues[j]
        print('Leave One Out OnlineParameter ', OnlineParameter)
        romLO.Predict(OnlineTimeSeq, OnlineParameter)
    
        error[j] = np.linalg.norm(snaps[j] - romLO.GetSnapOnline())
    
    print('Leave One Out error ', error)


    #calcualtion of next points in the parameter space. Initial simplex has to be convex.
    points = np.array(ParametersValues)
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




