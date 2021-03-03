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
                         "sigma": "SIEF_ELGA",
                         "Fext" : "FORC_NODA",
                         "r"    : "REAC_NODA"}

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
        if fieldName in ("U", "Fext", "r"):
            mlfield = ML.ReadFieldNode(self.fileName, meshName, 0, MED_field_name, iteration, order)
        if fieldName == "sigma":
            mlfield = ML.ReadFieldGauss(self.fileName, meshName, 0, MED_field_name, iteration, order)
        return mlfield

    def ReadSnapshotComponentNoFlatten(self, fieldName, time, primality):
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
        return data_array_double.toNumPyArray()

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
        return self.ReadSnapshotComponentNoFlatten(fieldName, time, primality).flatten()

    def WriteReducedOrderBasis(self, reducedOrderBasis, fieldName, fieldInstance, fileName):
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
        
        ff=ML.MEDFileFieldMultiTS.New()
        mf_mesh = ML.MEDFileUMesh.New(self.fileName)
        for imode in range(numberOfModes):
            f = safe_clone(fieldInstance)
            f.setTime(float(imode+1), imode+1, imode+1)
            if fieldName == "U":
                f.getArray().setInfoOnComponent(0, "DX")
                f.getArray().setInfoOnComponent(1, "DY")
                f.getArray().setInfoOnComponent(2, "DZ")
            if fieldName == "sigma":
                f.getArray().setInfoOnComponent(0, "SIXX")
                f.getArray().setInfoOnComponent(1, "SIYY")
                f.getArray().setInfoOnComponent(2, "SIZZ")
                f.getArray().setInfoOnComponent(3, "SIXY")
                f.getArray().setInfoOnComponent(4, "SIXZ")
                f.getArray().setInfoOnComponent(5, "SIYZ")
                f.getArray().setInfoOnComponent(6, "N")

            f.setName("base____" + self.Mordicus2MEDAster[fieldName])
            
            # array needs to be put to the right shape and converted to DataArrayDouble
            f.getArray().setValues(list(reducedOrderBasis[imode,:]), f.getNumberOfTuples(), f.getNumberOfComponents())
            
            # write f to a new file
            ff.appendFieldNoProfileSBT(f)

        mf_mesh.write(fileName, 2)
        ff.write(fileName, 0)
    
    def WriteSparseFieldOfEmpiricalWeights(self, np_coor_gauss, empirical_weights, fileName, fieldInstance):
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

        mf_mesh = ML.MEDFileUMesh.New(self.fileName)
        ff=ML.MEDFileField1TS.New()
        ff.setFieldNoProfileSBT(f)
        
        mf_mesh.write(fileName, 2)
        ff.write(fileName, 0)

    def WriteSolution(self, solution, fieldInstance, fieldName, fileName, name=None, append=False):
        """Convert a Mordicus snapshot into a MED field, with a field instance giving the structure"""
        numberOfSnapshots = solution.GetNumberOfSnapshots()
        
        ff=ML.MEDFileFieldMultiTS.New()
        if not append:
            mf_mesh = ML.MEDFileUMesh.New(self.fileName)

        for i, t in enumerate(solution.GetTimeSequenceFromSnapshots()):
            f = safe_clone(fieldInstance)
            f.setTime(t, i+1, i+1)
            
            # No need to do anything for the name ?
            if name is not None:
                target = "_"*8
                expanded_name = name[:min(8,len(name))] + target[min(8,len(name)):]
                f.setName(expanded_name + self.Mordicus2MEDAster[fieldName])
            if fieldName == "U":
                f.getArray().setInfoOnComponent(0, "DX")
                f.getArray().setInfoOnComponent(1, "DY")
                f.getArray().setInfoOnComponent(2, "DZ")
            if fieldName == "sigma":
                f.getArray().setInfoOnComponent(0, "SIXX")
                f.getArray().setInfoOnComponent(1, "SIYY")
                f.getArray().setInfoOnComponent(2, "SIZZ")
                f.getArray().setInfoOnComponent(3, "SIXY")
                f.getArray().setInfoOnComponent(4, "SIXZ")
                f.getArray().setInfoOnComponent(5, "SIYZ")
                f.getArray().setInfoOnComponent(6, "N")

            f.getArray().setValues(list(solution.GetSnapshot(t)), f.getNumberOfTuples(), f.getNumberOfComponents())

            # setArray is almost always a bad idea
            #f.setArray(ml.DataArrayDouble(solution.GetSnapshot(t)))
            # write f to a new file
            ff.appendFieldNoProfileSBT(f)
        if not append:
            mf_mesh.write(fileName, 2)
        ff.write(fileName, 0)

    def WriteNumbering(self, fieldInstance, fieldName, fileName, name=None):
        """
        Write an identity application on the input, see how it comes out to have the permutation matrix
        """
        mf_mesh = ML.MEDFileUMesh.New(self.fileName)

        f = safe_clone(fieldInstance)
        f.setTime(0.0, 0, 0)
        if fieldName == "U":
            f.getArray().setInfoOnComponent(0, "DX")
            f.getArray().setInfoOnComponent(1, "DY")
            f.getArray().setInfoOnComponent(2, "DZ")
        if fieldName == "sigma":
            f.getArray().setInfoOnComponent(0, "SIXX")
            f.getArray().setInfoOnComponent(1, "SIYY")
            f.getArray().setInfoOnComponent(2, "SIZZ")
            f.getArray().setInfoOnComponent(3, "SIXY")
            f.getArray().setInfoOnComponent(4, "SIXZ")
            f.getArray().setInfoOnComponent(5, "SIYZ")
            f.getArray().setInfoOnComponent(6, "N")

        if name is not None:
            target = "_"*8
            expanded_name = name[:min(8,len(name))] + target[min(8,len(name)):]
            f.setName(expanded_name + self.Mordicus2MEDAster[fieldName])
            
        # array needs to be put to the right shape and converted to DataArrayDouble
        identity_appl = np.linspace(0.,
                                    float(f.getNumberOfTuples()*f.getNumberOfComponents()-1),
                                    f.getNumberOfTuples()*f.getNumberOfComponents())
        f.getArray().setValues(list(identity_appl), f.getNumberOfTuples(), f.getNumberOfComponents())
            
        # write f to a new file
        ff=ML.MEDFileField1TS.New()
        ff.setFieldNoProfileSBT(f)

        mf_mesh.write(fileName, 2)
        ff.write(fileName, 0)
        