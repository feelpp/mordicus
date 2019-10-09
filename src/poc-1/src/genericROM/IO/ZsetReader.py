# -*- coding: utf-8 -*-
import numpy as np

from genericROM.IO.ReaderBase import ReaderBase
from BasicTools.IO import ZebulonIO as ZIO

    

def ReadSnapshot(solutionFileName, fieldName, time, primality = True):
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
    reader = ZsetReader(solutionFileName = solutionFileName)
    return reader.ReadSnapshot(fieldName, time, primality)


def ReadMesh(meshFileName):
    """
    Functional API
    
    Reads the mesh defined the Z-set mesh file "meshFileName" (.geof or .geo)
            
    Parameters
    ----------
    meshFileName : str
        Z-set mesh file 
                    
    Returns
    -------
    BasicToolsUnstructuredMesh
        mesh of the HF computation
    """
    reader = ZsetReader(meshFileName = meshFileName)
    return reader.ReadMesh()


def ReadInputTimeSequence(inputFileName):
    """
    Functional API
    
    Reads the time sequence from the Z-set input file "inputFileName" (.inp) (may be different from the ones defined in the solution file if the solver chose to solve at additional time steps)
            
    Parameters
    ----------
    inputFileName : str
        Z-set input file 
                
    Returns
    -------
    np.ndarray
        of size (numberOfSnapshots,)
    """
    reader = ZsetReader(inputFileName = inputFileName)
    return reader.ReadInputTimeSequence()


def ReadTimeSequenceFromSolutionFile(solutionFileName):
    """
    Reads the time sequence from the Z-set solution file "solutionFileName" (.ut) (may be different from the ones defined in the input data file if the solver chose to solve at additional time steps)
            
    Parameters
    ----------
    solutionFileName : str
        Z-set solution file 
    
    Returns
    -------
    np.ndarray
        of size (numberOfSnapshots,)
    """
    reader = ZsetReader(solutionFileName = solutionFileName)
    return reader.ReadTimeSequenceFromSolutionFile()


def ConstructLoadingsList(inputFileName):
    """
    Constructs the loadings defined in the Z-set input file "inputFileName" (.inp)
            
    Parameters
    ----------
    inputFileName : str
        Z-set input file 
    
    Returns
    -------
    list
        list of loadings, each one having one of the formats defined in Containers.Loadings
    """    
    reader = ZsetReader(inputFileName = inputFileName)
    return reader.ConstructLoadingsList()



class ZsetReader(ReaderBase):
    """
    Class containing a reader for Z-set input, mesh and solution files

    Attributes
    ----------
    inputFileName : str
        name of the Z-set input file (.inp)
    meshFileName : str
        name of the Z-set mesh file (.geof or .geo)
    solutionFileName : str
        name of the Z-set solution file (.ut)
    inputFile : list
        list containing the input file as parsed by BasicTools.IO.ZebulonIO
    knownLoadingTags : list
        list of loadings tags in the Z-set input file that have been implemented in the current version of the library
    """
    
    def __init__(self, inputFileName = None, meshFileName = None, solutionFileName = None):
        """
        Parameters
        ----------
        inputFileName : str, optional
        meshFileName : str, optional
        solutionFileName : str, optional
        """
        super(ZsetReader,self).__init__()
        
        assert isinstance(inputFileName,str) or inputFileName is None
        assert isinstance(meshFileName,str) or meshFileName is None
        assert isinstance(solutionFileName,str) or solutionFileName is None
        
        self.inputFileName    = inputFileName
        self.meshFileName     = meshFileName
        self.solutionFileName = solutionFileName        
        self.inputFile        = None

        self.knownLoadingTags  = ["pressure"]
        
        
    def SetInputFile(self):
        """
        Sets the inputFile using the parser in BasicTools.IO.ZebulonIO
        """
        if self.inputFile == None:
            self.inputFile = ZIO.ReadInp2(self.inputFileName)
        else:
            return
        
        
    def ReadSnapshot(self, fieldName, time, primality= True):
        from BasicTools.IO import UtReader as UR
        if primality == True:
            atIntegrationPoints = False
        else:
            atIntegrationPoints = True#pragma: no cover
        return UR.ReadFieldFromUt(self.solutionFileName, fieldName, time, atIntegrationPoints = atIntegrationPoints)        



    def ReadMesh(self):
        """
        Read the mesh of the HF computation
                    
        Returns
        -------
        BasicToolsUnstructuredMesh
            mesh of the HF computation
        """
        if self.meshFileName[-5:] == ".geof":
            from BasicTools.IO import GeofReader as GR
            data = GR.ReadGeof(self.meshFileName)
        elif self.meshFileName[-4:] == ".geo": #pragma: no cover
            from BasicTools.IO import GeoReader as GR
            data = GR.ReadGeo(self.meshFileName)
        else: #pragma: no cover
            raise("FileName error!")
            
        from genericROM.Containers.Meshes import BasicToolsUnstructuredMesh as BTUM
        mesh = BTUM.BasicToolsUnstructuredMesh(data)

        return mesh



    def ReadInputTimeSequence(self):
        self.SetInputFile()
        return ZIO.GetInputTimeSequence(self.inputFile)
                
                
    
    def ReadTimeSequenceFromSolutionFile(self):
        from BasicTools.IO import UtReader as UR
        UTMetaData = UR.ReadUTMetaData(self.solutionFileName)
        return UTMetaData["time"][:,4]
    
                
        
    def ConstructLoadingsList(self):
        import os
        
        self.SetInputFile()
        tables = ZIO.GetTables(self.inputFile)
        bcs = ZIO.GetBoundaryConditions(self.inputFile)

        loadings = []
        for key, value in bcs.items():
            if key in self.knownLoadingTags:
                for bc in bcs[key]:
                    loadings.append(self.ConstructOneLoading(key, bc, tables))
            else:
                print("Boundary Condition '"+key+"' not among knownBCs: "+str([key for key in self.knownLoadingTags]))
                
        return loadings

        

    def ConstructOneLoading(self, key, bc, tables):
        """
        Constructs one loading from the Zset input file

        Parameters
        ----------
        key : str
            Zset keyword for the loading
        bc : list
            list containing the boundary condition data as defined in BasicTools.IO.ZebulonIO
        tables : dict
            list containing the tables data as defined in BasicTools.IO.ZebulonIO
            
        Returns
        -------
        LoadingBase
            the constructed loading in one of the formats defined in Containers.Loadings
        """
        
        import collections
        import os
            
        if key == "pressure":
            from genericROM.Containers.Loadings import PressureBC

            loading = PressureBC.PressureBC()
            
            loading.SetSet(bc[0][0])
            
            sequence = tables[bc[0][3]]
            name = os.path.dirname(self.inputFileName)+os.sep+bc[0][2]
            
            coefficients = collections.OrderedDict()
            fieldsMap = collections.OrderedDict()
            for i, time in enumerate(sequence["time"]):
                coefficients[float(time)] = sequence["value"][i]
                fieldsMap[float(time)] = name
                
            loading.SetCoefficients(coefficients)
            loading.SetFieldsMap(fieldsMap)
                
            fields = {name:ZIO.ReadBinaryFile(name)}
                        
            loading.SetFields(fields)
            
            return loading
            



def CheckIntegrity():

    import genericROM.TestData as genericROMToolsTestData

    folder = genericROMToolsTestData.GetTestDataPath()+"Zset/"
    
    inputFileName = folder + "cube.inp"
    meshFileName = folder + "cube.geof"
    solutionFileName = folder + "cube.ut"
    
    reader = ZsetReader(inputFileName, meshFileName, solutionFileName)
    
    inputTimeSequence = reader.ReadInputTimeSequence()
    inputTimeSequence = ReadInputTimeSequence(inputFileName)
    
    snapshot = reader.ReadSnapshot("U1", inputTimeSequence[0], primality = True)
    snapshot = ReadSnapshot(solutionFileName, "U1", inputTimeSequence[0], primality = True)

    mesh = reader.ReadMesh()
    mesh = ReadMesh(meshFileName)

    outputTimeSequence = reader.ReadTimeSequenceFromSolutionFile()
    outputTimeSequence = ReadTimeSequenceFromSolutionFile(solutionFileName)

    loadings = reader.ConstructLoadingsList()
    loadings = ConstructLoadingsList(inputFileName)
    
    return "ok"


if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
