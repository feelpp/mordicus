# -*- coding: utf-8 -*-
import numpy as np
from core.Containers.BaseObject import BaseObject


class ReaderBase(BaseObject):
    """
    Class containing the ReaderBase associated to a HF computation
    """
    
    def __init__(self):
        super(ReaderBase,self).__init__()



    def ReadSnapshot(self, fieldName, time, primality):
        """
        Reads a snapshots from the solutions of name "fieldName", at time "time" and of primality "primality", from the HF computation
    
        Parameters
        ----------
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
        raise("Not implemented in ReaderBase")  #pragma: no cover 
    
    

    def ReadMesh(self):
        """
        Reads the mesh of the HF computation
                    
        Returns
        -------
        MeshBase
            mesh in one of the formats defined in Containers.Meshes
        """
        raise("Not implemented in ReaderBase")  #pragma: no cover  


        
    def ReadInputTimeSequence(self):
        """
        Reads the time sequence from the input data file of the HF computation (may be different from the ones defined in the solution file if the solver chose to solve at additional time steps)
                    
        Returns
        -------
        np.ndarray
            of size (numberOfSnapshots,)
        """
        raise("Not implemented in ReaderBase")  #pragma: no cover  


        
    def ReadTimeSequenceFromSolutionFile(self):
        """
        Reads the time sequence from the solution file of the HF computation (may be different from the ones defined in the input data file if the solver chose to solve at additional time steps)
        
        Returns
        -------
        np.ndarray
            of size (numberOfSnapshots,)
        """
        raise("Not implemented in ReaderBase")  #pragma: no cover  


        
    def ConstructLoadingsList(self):
        """
        Constructs the loadings defined in the input data file of the HF computation
        
        Returns
        -------
        list
            list of loadings, each one having one of the formats defined in Containers.Loadings
        """
        raise("Not implemented in ReaderBase")  #pragma: no cover  



    def __str__(self):
        from .. import IO
        allIO = IO.__all__
        allReaders = [a for a in allIO if ("Reader" in a and "Base" not in a)]
        res = "I am a ReaderBase, try instanciating a particular reader "+str(allReaders)+" instead"
        return res



def CheckIntegrity():

    readerBase = ReaderBase()
    print(readerBase)
    return "ok"



if __name__ == '__main__':
    print(CheckIntegrity()) #pragma: no cover
