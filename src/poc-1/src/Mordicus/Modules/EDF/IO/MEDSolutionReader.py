# coding: utf-8
from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
import medcoupling as ml
import MEDLoader as ML
import numpy as np
from Mordicus.Modules.EDF.Containers.FieldHandlers.MEDFieldHandler import safe_clone

class MEDSolutionReader(SolutionReaderBase):
    """
    Class to convert MEDSolution into ProblemData
    """
    Mordicus2MEDAster = {"U"    : "DEPL",
                         "sigma": "SIEF_ELGA"}

    def __init__(self, fileName):
        '''
        Constructor
        '''
        super(MEDSolutionReader, self).__init__()
        self.fileName = fileName

    def ReadTimeSequenceFromSolutionFile(self, fieldName):
        """Override from SolutionReaderBase"""
        # TODO: demander en comité technique à ajouter fieldName à ReadTimeSequenceFromSolutionFile
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        return np.array([it[2] for it in all_iterations])

    def _extract_name_and_sequence(self, fieldName):
        """
        Returns the MED name of the field as well as all time iterations for this field
        """
        # Recuperer le nom MED du champ
        all_field_names = ML.GetAllFieldNames(self.fileName)
        try:
            MED_field_name = next(n for n in all_field_names if n.endswith(self.Mordicus2MEDAster[fieldName]))
        except StopIteration:
            raise IOError("File {0} does not contain a field whose name ends with {1}".format(self.fileName, 
                    self.Mordicus2MEDAster[fieldName]))
        # Trouver (iteration, order) qui correspond au pas de temps
        all_iterations = ML.GetAllFieldIterations(self.fileName, MED_field_name)
        return all_iterations, MED_field_name


    def readMEDField(self, fieldName, time):
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        iteration, order = next((a, b) for (a, b, c) in all_iterations if c == time)
    # Lecture du resultat pour le bon nom de champ et de temps
        meshName = ML.GetMeshNames(self.fileName)[0]
        if fieldName == "U":
            mlfield = ML.ReadFieldNode(self.fileName, meshName, 0, MED_field_name, iteration, order)
        if fieldName == "sigma":
            mlfield = ML.ReadFieldGauss(self.fileName, meshName, 0, MED_field_name, iteration, order)
        return mlfield

    def ReadSnapshotComponent(self, fieldName, time, primality):
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
        mlfield = self.readMEDField(fieldName, time)
        data_array_double = mlfield.getArray()
        return data_array_double.toNumPyArray().flatten()

    @classmethod
    def WriteReducedOrderBasis(cls, reducedOrderBasis, fieldName, fieldInstance, fileName):
        """
        Converts Mordicus reduced order basis into the MED format
        
        Parameters
        ----------
        reducedOrderBasis : nparray(numberOfModes, numberOfDofs)
            numpy array of the modes
        fieldName : str
            name of field associated with the basis (e.g. "U", "sigma")
        fieldInstance : MEDCouplingField
            instance of field to give the structure for the modes
        fileName : str
            
        """
        numberOfModes, _ = reducedOrderBasis.shape
        for imode in range(numberOfModes):
            f = safe_clone(fieldInstance)
            f.setTime(float(imode), imode, imode)
            f.setName("base____" + cls.Mordicus2MEDAster[fieldName])
            
            # array needs to be put to the right shape and converted to DataArrayDouble
            f.getArray().setValues(list(reducedOrderBasis[imode,:]), f.getNumberOfTuples(), f.getNumberOfComponents())
            
            # write f to a new file
            if imode == 0:
                ML.WriteField(fileName, f, True)
            else:
                ML.WriteFieldUsingAlreadyWrittenMesh(fileName, f)
    
    @classmethod
    def WriteSparseFieldOfEmpiricalWeights(cls, np_coor_gauss, empirical_weights, fileName, fieldInstance):
        """
        Writes found empirical_weights to a Gauss MED field
        
        Parameters
        ----------
        np_coor_gauss
            numpy array of empirical Gauss points
        empirical_weights
            numpy array of empirical weights
        """
        import numpy as np
        # another solution would be to clone the field and replace the array, but this one seems cleaner
        f = ml.MEDCouplingFieldDouble.New(ml.ON_GAUSS_PT, ml.ONE_TIME)
        f.setMesh(fieldInstance.getMesh())
        f.setName("W_EMPI__")
        f.setTime(0.0, 0, 0)
        
        for i_gauss_loc in range(fieldInstance.getNbOfGaussLocalization()):
            gauss_loc = fieldInstance.getGaussLocalization(i_gauss_loc)
            cell_type, refCoo, gsCoo, wg = gauss_loc.getType(), gauss_loc.getRefCoords(), gauss_loc.getGaussCoords(), gauss_loc.getWeights()
            f.setGaussLocalizationOnType(cell_type, refCoo, gsCoo, wg)

        # 1 component per Gauss point, initiated to 0
        f.fillFromAnalytic(1, "0")

        # indices of non zero empirical_weights
        nonzero_indices = empirical_weights.nonzero()[0]
        print("nonzero_indices = ", nonzero_indices)
        char_len = fieldInstance.getMesh().getCaracteristicDimension()
        
        gauss_pts = fieldInstance.getLocalizationOfDiscr().toNumPyArray()
        nb_comps = gauss_pts.shape[1]
        
        # for each, find Gauss location, set field value there
        for i_nonzero in nonzero_indices:

            f.getArray().toNumPyArray()[i_nonzero] = np.double(empirical_weights[i_nonzero])
            dist = 0.
            for i_comp in range(nb_comps):
                dist = dist + (gauss_pts[i_nonzero, i_comp]-np_coor_gauss[i_nonzero, i_comp])**2
            dist = np.sqrt(dist)
            if dist > 1.e-8*char_len:
                raise ValueError("The sample field provided for empirical weights is numbered differently")
        f.getArray().setInfoOnComponent(0, "X1")
        
        ML.WriteField(fileName, f, True)

    def WriteSolution(self, solution, fieldInstance, fieldName, fileName, name=None):
        """Convert a Mordicus snapshot into a MED field, with a field instance giving the structure"""
        numberOfSnapshots = solution.GetNumberOfSnapshots()
        for i, t in enumerate(solution.GetTimeSequenceFromSnapshots()):
            f = safe_clone(fieldInstance)
            f.setTime(t, i+1, i+1)
            
            # No need to do anything for the name ?
            if name is not None:
                target = " "*8
                expanded_name = name[:min(8,len(name))] + target[min(8,len(name)):]
                f.setName(expanded_name + self.Mordicus2MEDAster[fieldName])

            f.setArray(ml.DataArrayDouble(solution.GetSnapshot[t]))
            # write f to a new file
            if i == 0:
                ML.WriteField(fileName, f, True)
            else:
                ML.WriteFieldUsingAlreadyWrittenMesh(fileName, f)
        
        
    def ReadSnapshotComponentAtMask(self, fieldName, time, primality, fieldWeights):
        """Reads snapshot coordinates at mask"""
        # A line to retrieve the field of weights if necessary
        # poid_field = ML.ReadFieldGauss("/home/A34370/tmp/arcad01a_to_m_fiel.rmed", "MAILR", 0, 'POIDR', -1, -1)
        nonzero_terms = np.nonzero(fieldWeights.getArray().toNumPyArray())
        full_vec = self.ReadSnapshotComponent(fieldName, time, primality)
        return full_vec[nonzero_terms,:]

        