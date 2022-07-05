# coding: utf-8
import math

from Mordicus.Core.IO.SolutionReaderBase import SolutionReaderBase
import medcoupling as ml
import MEDLoader as ML
import numpy as np

from Mordicus.Modules.EDF.IO.MEDMesh import MEDMesh
from Mordicus.Modules.EDF.Containers.FieldHandlers.MEDFieldHandler import safe_clone
from Mordicus.Modules.EDF.Containers.SolutionStructures.MEDAsterSolutionStructure import MEDAsterSolutionStructure

class MEDSolutionReader(SolutionReaderBase):
    """
    Class to convert MEDSolution into ProblemData
    """
    Mordicus2MEDAster = {"U"    : "DEPL",
                         "sigma": "SIEF_ELGA",
                         "Fext" : "FORC_NODA",
                         "r"    : "REAC_NODA"}
    
    Disc2MLType = {"nodes": ML.ON_NODES,
                   "gauss": ML.ON_GAUSS_PT}

    def __init__(self, fileName, timeIt):
        '''
        Constructor
        
        Arguments
        ---------
        fileName : str
            File name to read solutions from
        timeIt : float
            time for loading a reference field
        '''
        super(MEDSolutionReader, self).__init__()
        self.fileName = fileName
        self.timeIt = timeIt

    def ReadTimeSequenceFromSolutionFile(self, fieldName):
        """
        Overriden from SolutionReaderBase
        """
        # TODO: demander en comité technique à ajouter fieldName à ReadTimeSequenceFromSolutionFile
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        return np.array([it[2] for it in all_iterations])

    def _extract_name_and_sequence(self, fieldName):
        """
        Returns the MED name of the field as well as all time iterations for this field

        fieldName : str
            name of the solution from which the snapshot is read (e.g. "U", "sigma")
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

    def ReadSnapshotComponent(self, fieldName, time, primality, solutionStructure):
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
        solutionStructure : SolutionStructure
            solution structure to guide putting the result into array
                    
        Returns
        -------
        np.ndarray
            of size (numberOfDofs,)
        """
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        iteration, order = next((a, b) for (a, b, c) in all_iterations if math.isclose(c, time))
        
        # read the field under the form of a MEDFileField1TS
        f1ts = ML.MEDFileField1TS(self.fileName, MED_field_name, iteration, order)
        mfMeshName = f1ts.getMeshName()
        mf_mesh = ML.MEDFileUMesh.New(self.fileName, mfMeshName)
        
        fieldInstances = solutionStructure.GetInternalStorage()

        start = True
        for relLevel, (fieldInstance, idsInRelLevel) in fieldInstances.items():
            disc = fieldInstance.getTypeOfField()
            f = f1ts.getFieldOnMeshAtLevel(disc, relLevel, mf_mesh)

            # Select groups if necessary
            if idsInRelLevel is not None:
                if solutionStructure.discr in ("gauss", "cell"):
                    f = f.buildSubPart(idsInRelLevel)
                if solutionStructure.discr in ("node", ):
                    f.setArray(f.getArray()[idsInRelLevel].deepCopy())

            compos_num_to_select = [f.getArray().getInfoOnComponents().index(c) for c in fieldInstance.getArray().getInfoOnComponents()]
            f = f.keepSelectedComponents(compos_num_to_select)
            if not start:
                res = np.concatenate((res, f.getArray().toNumPyArray().flatten()))
            if start:
                res = f.getArray().toNumPyArray().flatten()
                start = False                
          
        return res

    def WriteReducedOrderBasis(self, fileName, solutionStructure, reducedOrderBasis, fieldName):
        """
        Converts Mordicus reduced order basis into the MED format
        
        Parameters
        ----------
        fileName : str
            MED file to write reduced basis to
        fieldStructure : MEDAsterSolutionStructure
            field structure giving the context to interpret the vector in terms of field values on the mesh
        reducedOrderBasis : nparray(numberOfModes, numberOfDofs)
            numpy array of the modes
        fieldName : str
            name of field associated with the basis (e.g. "U", "sigma")         
        """
        fieldInstances = solutionStructure.GetInternalStorage()
        
        mf_mesh_strip = ML.MEDFileUMesh.New()
        mf_mesh_strip.setName("MeshStripped")

        for relLevel, (fieldInstance, _) in fieldInstances.items():
            mc_mesh_at_level = fieldInstance.getMesh()
            mc_mesh_at_level.setName("MeshStripped")
            mf_mesh_strip.setMeshAtLevel(relLevel, mc_mesh_at_level)
            
        if solutionStructure.discr in ("gauss", "cell"):
            mf_mesh_strip.zipCoords()

        numberOfModes, _ = reducedOrderBasis.shape
        
        f_mts=ML.MEDFileFieldMultiTS.New()
        f_mts.setName("base____" + self.Mordicus2MEDAster[fieldName])

        for imode in range(numberOfModes):
            offset = 0
            f1ts = ML.MEDFileField1TS.New()
            f1ts.setTime(imode+1, imode+1, float(imode+1))
            f1ts.setName("base____" + self.Mordicus2MEDAster[fieldName])

            for relLevel, (fieldInstance, _) in fieldInstances.items():           
                f = safe_clone(fieldInstance)
                f.setTime(float(imode+1), imode+1, imode+1)
                f.setName("base____" + self.Mordicus2MEDAster[fieldName])
            
                # array needs to be put to the right shape and converted to DataArrayDouble
                offset_new = offset + f.getNumberOfTuples()*f.getNumberOfComponents()
                f.getArray().setValues(list(reducedOrderBasis[imode,offset:offset_new]), f.getNumberOfTuples(), f.getNumberOfComponents())
                offset = offset_new
                # write f to a new file
                f1ts.setFieldNoProfileSBT(f)
            
            f_mts.pushBackTimeStep(f1ts)

        mf_mesh_strip.write(fileName, 2)
        f_mts.write(fileName, 0)
    
    def WriteSparseFieldOfEmpiricalWeights(self, fileName, fieldStructure, np_coor_gauss, empirical_weights):
        """
        Writes found empirical_weights to a Gauss MED field
        
        Parameters
        ----------
        fileName : str
            MED file to write field of empirical weights to
        fieldStructure : MEDAsterSolutionStructure
            field structure giving the context to interpret the vector in terms of field values on the mesh
        np_coor_gauss
            numpy array of empirical Gauss points coordinates
        empirical_weights
            numpy array of empirical weights
        """
        import numpy as np
        if fieldStructure.discr != "gauss":
            raise ValueError("fieldStructure in argument to WriteSparseFieldOfEmpiricalWeights should be of type gauss.")
        fieldInstances = fieldStructure.GetInternalStorage()
        
        mf_mesh_strip = ML.MEDFileUMesh.New()
        mf_mesh_strip.setName("MeshStripped")

        for relLevel, (fieldInstance, _) in fieldInstances.items():
            mc_mesh_at_level = fieldInstance.getMesh()
            mc_mesh_at_level.setName("MeshStripped")
            mf_mesh_strip.setMeshAtLevel(relLevel, mc_mesh_at_level)
        mf_mesh_strip.zipCoords()

        f1ts=ML.MEDFileField1TS.New()
        f1ts.setTime(0, 0, 0.0)

        offset = 0
        for relLevel, (fieldInstance, _) in fieldInstances.items():
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
            offset_new = offset + f.getNumberOfTuples()

            # indices of non zero empirical_weights
            nonzero_indices = empirical_weights.nonzero()[0]
            char_len = fieldInstance.getMesh().getCaracteristicDimension()
        
            gauss_pts = fieldInstance.getLocalizationOfDiscr().toNumPyArray()
            nb_comps = gauss_pts.shape[1]
        
            # for each, find Gauss location, set field value there$
            f_non_zero_indices = nonzero_indices[np.where((nonzero_indices >= offset) & (nonzero_indices < offset_new))]
            for i_nonzero in f_non_zero_indices:
    
                f.getArray().toNumPyArray()[i_nonzero-offset] = np.double(empirical_weights[i_nonzero])
                dist = 0.
                for i_comp in range(nb_comps):
                    dist = dist + (gauss_pts[i_nonzero-offset, i_comp]-np_coor_gauss[i_nonzero, i_comp])**2
                dist = np.sqrt(dist)
                if dist > 1.e-8*char_len:
                    raise ValueError("The sample field provided for empirical weights is numbered differently")
            f.getArray().setInfoOnComponent(0, "X1")
            
            offset = offset_new

            f1ts.setFieldNoProfileSBT(f)
        
        mf_mesh_strip.write(fileName, 2)
        f1ts.write(fileName, 0)
        
    def WriteSolutionStructure(self, fileName, fieldStructure, fieldName):
        return self.WriteReducedOrderBasis(fileName,
                                           fieldStructure,
                                           np.zeros((1, fieldStructure.GetNumberOfNodes()*fieldStructure.GetNumberOfComponents())),
                                           fieldName)

    def WriteOperatorCompressionData(self, fileName, key, cpd):
        self.WriteSparseFieldOfEmpiricalWeights(fileName, cpd.solutionStructures["sigma"],
                                                cpd.operatorCompressionData[key][0],
                                                cpd.operatorCompressionData[key][1])


    def WriteSolution(self, fileName, fieldStructure, solution, fieldName, nameInFile=None, append=False):
        """
        Convert a Mordicus snapshot into a MED field, relying on SolutionStructure to build relations
        between the vector of values and the mesh.
        
        Arguments
        ---------
        fileName : str
            MED file to write solution to
        fieldStructure : MEDAsterSolutionStructure
            field structure giving the context to interpret the vector in terms of field values on the mesh
        solution : Solution
            solution to write
        fieldName : str
            identifier of the physical quantity for the field
        nameInFile : str
            to customize field name in output MED file *fileName*
        append : bool
            if true results are appended to fileName and mesh is not written (again). Otherwise fileName is written from scratch
        """
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        
        f_mts = ML.MEDFileFieldMultiTS.New()
        fieldInstances = fieldStructure.GetInternalStorage()

        for i, t in enumerate(solution.GetTimeSequenceFromSnapshots()):
            iteration, order = next((a, b) for (a, b, c) in all_iterations if math.isclose(c, t))
        
            # read the field under the form of a MEDFileField1TS
            f1ts = ML.MEDFileField1TS(self.fileName, MED_field_name, iteration, order)
            f1ts.setTime(i+1, i+1, t)
            mf_disc, = f1ts.getTypesOfFieldAvailable()
            if i == 0:
                mfMeshName = f1ts.getMeshName()
                mf_mesh = ML.MEDFileUMesh.New(self.fileName, mfMeshName)
            
            offset = 0
            for relLevel, (fieldInstance, idsInRelLevel) in fieldInstances.items():

                # start with background 0 field all over
                mc_field_bg = f1ts.getFieldOnMeshAtLevel(mf_disc, relLevel, mf_mesh)
                mc_field_bg.getArray().fillWithValue(0.0)

                mc_field_bg.setTime(t, i+1, i+1)
                
                f = safe_clone(fieldInstance)
                f.setTime(t, i+1, i+1)
                
                # reduce number of components all over
                compos_num_to_select = [mc_field_bg.getArray().getInfoOnComponents().index(c) for c in f.getArray().getInfoOnComponents()]
                
                # The following truncates the field: not the desired behavior, we want to leave unselected components to their older values
                #mc_field_bg = mc_field_bg.keepSelectedComponents(compos_num_to_select)
                has_component_selection = len(compos_num_to_select) < mc_field_bg.getNumberOfComponents()
    
                if nameInFile is not None:
                    target = "_"*8
                    expanded_name = nameInFile[:min(8,len(nameInFile))] + target[min(8,len(nameInFile)):]
                    mc_field_bg.setName(expanded_name + self.Mordicus2MEDAster[fieldName])
                    
                f.setName(mc_field_bg.getName())
                f1ts.setName(mc_field_bg.getName())
                f_mts.setName(mc_field_bg.getName())
    
                # array needs to be put to the right shape and converted to DataArrayDouble
                offset_new = offset + f.getNumberOfTuples()*f.getNumberOfComponents()
                f.getArray().setValues(list(solution.GetSnapshot(t)[offset:offset_new]),
                                       f.getNumberOfTuples(), f.getNumberOfComponents())
                offset = offset_new
                
                # put that into mc_field_bg
                if idsInRelLevel is not None:
                    if fieldStructure.discr in ("gauss", "cell"):
                        tupIds = mc_field_bg.computeTupleIdsToSelectFromCellIds(idsInRelLevel)
                    if fieldStructure.discr in ("node", ):
                        tupIds = idsInRelLevel
                        
                    # command in case there is no components selection
                    if not has_component_selection:
                        mc_field_bg.getArray()[tupIds] = f.getArray().deepCopy()
                    if has_component_selection:
                        mc_field_bg.getArray().toNumPyArray()[tupIds,np.array(compos_num_to_select)] = f.getArray().deepCopy().toNumPyArray()
                
                else:
                    # The following is native Medcoupling syntax but it s unclear whether it still works
                    #     if the N components to keep are not the first N components
                    # There seems to be a setPartOfValues2 function in later versions of medcoupling
                    # Not using it for now
                    #mc_field_bg.getArray().setPartOfValues1(f.getArray().deepCopy(), 0, f.getNumberOfTuples(), 1, 0, f.getNumberOfComponents(), 1)
                    
                    if not has_component_selection:
                        f1ts.setFieldNoProfileSBT(f)
                        continue
                    if has_component_selection:
                        mc_field_bg.getArray().toNumPyArray()[:,np.array(compos_num_to_select)] = f.getArray().deepCopy().toNumPyArray()

                f1ts.setFieldNoProfileSBT(mc_field_bg)

            # setArray is almost always a bad idea
            f_mts.pushBackTimeStep(f1ts)

        if not append:
            mf_mesh.write(fileName, 2)
        f_mts.write(fileName, 0)

    def WriteNumbering(self, fileName, fieldStructure, fieldName, nameInFile=None):
        """
        Write an identity application on the input, gets the permutation application on the output.
        This method is used to convert operators from a FEM code to the numbering system associated
            with the format of the results (for instance be able to get a consistent numbering between
            a mass matrix computed with Code_Aster and the results written to MED format)
            
        Arguments
        ---------
        fileName : str
            MED file to write permutation to
        fieldStructure : MEDAsterSolutionStructure
            field structure for which the numbering system has to be converted
        fieldName : str
            identifier of the physical quantity for the field
        nameInFile : str
            to customize field name in output MED file *fileName*
        """
        # --- find right field to import by name and iteration
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        iteration, order = next((a, b) for (a, b, c) in all_iterations if math.isclose(c, self.timeIt))
        
        # read the field under the form of a MEDFileField1TS
        mf_field_bg = ML.MEDFileField1TS(self.fileName, MED_field_name, iteration, order)
        mf_disc, = mf_field_bg.getTypesOfFieldAvailable()
        mfMeshName = mf_field_bg.getMeshName()
        mf_mesh = ML.MEDFileUMesh.New(self.fileName, mfMeshName)

        ff=ML.MEDFileField1TS.New()
        ff.setTime(0, 0, 0.0)
                    
        fieldInstances = fieldStructure.GetInternalStorage()

        offset = 0
        for relLevel, (fieldInstance, idsInRelLevel) in fieldInstances.items():

            
            # start with background -1 field all over
            mc_field_bg = mf_field_bg.getFieldOnMeshAtLevel(mf_disc, relLevel, mf_mesh)
            
            # do not use mc_field_bg.fillWithAnalytic !! For some reaseon it erases info on components
            mc_field_bg.getArray().fillWithValue(-1.0)
            mc_field_bg.setTime(0.0, 0, 0)
            
            f = safe_clone(fieldInstance)
            f.setTime(0.0, 0, 0)
            
            # reduce number of components all over
            #print("the infos : ", mc_field_bg.getArray().getInfoOnComponents())
            compos_num_to_select = [mc_field_bg.getArray().getInfoOnComponents().index(c) for c in f.getArray().getInfoOnComponents()]
            mc_field_bg = mc_field_bg.keepSelectedComponents(compos_num_to_select)

            if nameInFile is not None:
                target = "_"*8
                expanded_name = nameInFile[:min(8,len(nameInFile))] + target[min(8,len(nameInFile)):]
                mc_field_bg.setName(expanded_name + self.Mordicus2MEDAster[fieldName])
                
            f.setName(mc_field_bg.getName())
            ff.setName(mc_field_bg.getName())

            # array needs to be put to the right shape and converted to DataArrayDouble
            identity_appl = np.linspace(float(offset),
                                        float(offset-1+f.getNumberOfTuples()*f.getNumberOfComponents()),
                                        f.getNumberOfTuples()*f.getNumberOfComponents())
            f.getArray().setValues(list(identity_appl), f.getNumberOfTuples(), f.getNumberOfComponents())
            offset = offset + f.getNumberOfTuples()*f.getNumberOfComponents()
            
            # put that into mc_field_bg
            if idsInRelLevel is not None:
                if fieldStructure.discr in ("gauss", "cell"):
                    tupIds = mc_field_bg.computeTupleIdsToSelectFromCellIds(idsInRelLevel)
                if fieldStructure.discr in ("node", ):
                    tupIds = idsInRelLevel
                mc_field_bg.getArray()[tupIds] = f.getArray().deepCopy()
            
                # write f to a new file
                ff.setFieldNoProfileSBT(mc_field_bg)
            else:
                ff.setFieldNoProfileSBT(f)

        mf_mesh.write(fileName, 2)
        ff.write(fileName, 0)
        
    def ReadSolutionStructure(self, fieldName,
                              discretization,
                              components=[],
                              dimsRelativeToMax=[],
                              groups=[],
                              componentsByRelativeDimension=None):
        """
        Read the solution structure object. To move to MEDSolutionReader ?
        
        Arguments
        ---------
        fieldName : str
            identifier of the physical quantity for the field
        discretization : str
            type of field discretization. Into {"node", "gauss"} for now, to be expanded...
        components : list(str)
            list of components to select in the field. By default they are all kept
        dimsRelativeToMax : list(int)
            list of dimension of mesh entities to select relative to max dimension. Into {-3, -2, -1, 0}
        componentsByRelativeDimension : dict(int: list)
            dictionary of components to keep by relative dimension (relative to max dimension)
        groups :
            list of groups to keep. result is extracted on the union of these groups.
            
        Returns
        -------
        MEDAsterSolutionStructure
            A SolutionStructure for MEDAster
        """
        if discretization == "node":
            return self._readSolutionStructureNode(fieldName,
                                                   components,
                                                   dimsRelativeToMax,
                                                   groups)
        # --- find right field to import by name and iteration
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        iteration, order = next((a, b) for (a, b, c) in all_iterations if math.isclose(c, self.timeIt))      
        
        # read the field under the form of a MEDFileField1TS
        f1ts = ML.MEDFileField1TS(self.fileName, MED_field_name, iteration, order)

        mfMeshName = f1ts.getMeshName()
        mf_mesh = ML.MEDFileUMesh.New(self.fileName, mfMeshName)
        
        solutionStructure = MEDAsterSolutionStructure(MEDMesh(mf_mesh), "gauss")
        solutionStructureInternalStorage = {}
        
        # --- Loop over relative dimensions
        nonEmptyLevels = reversed(sorted(list(f1ts.getNonEmptyLevels()[1])))
        includedLevels = reversed(sorted(dimsRelativeToMax)) if dimsRelativeToMax else nonEmptyLevels
        
        walkedLevels = reversed(sorted(list( set(nonEmptyLevels).intersection(set(includedLevels)) )))
        
        for relLevel in walkedLevels:
            
            # extract list of groups that are non empty at this level
            groupSubset = groups
            if groups:
                groupSubset = [grp for grp in groups if relLevel in mf_mesh.getGrpNonEmptyLevels(grp)]

                if not groupSubset:
                    continue

            mc_field = f1ts.getFieldOnMeshAtLevel(self.Disc2MLType[discretization], relLevel, mf_mesh)
            
            # Select groups
            elemIdsInRelLevel = None
            if groups:
                elemIdsInRelLevel = mf_mesh.getGroupsArr(relLevel, groupSubset, False)
                mc_field = mc_field[elemIdsInRelLevel] # or mc_field = mc_field.buildSubPart(elemIdsInRelLevel)

            # Select components for this relative dimension
            if components or (componentsByRelativeDimension and componentsByRelativeDimension[relLevel]):
                list_of_compos = mc_field.getArray().getInfoOnComponents()
                compos_to_select = componentsByRelativeDimension[relLevel] if componentsByRelativeDimension and componentsByRelativeDimension[relLevel] \
                    else components
            
                compos_num_to_select = [list_of_compos.index(c) for c in compos_to_select]
                
                mc_field = mc_field.keepSelectedComponents(compos_num_to_select)
        
            solutionStructureInternalStorage[relLevel] = (mc_field, elemIdsInRelLevel)
        
        solutionStructure.SetInternalStorage(solutionStructureInternalStorage)
        return solutionStructure
    
    def _readSolutionStructureNode(self, fieldName,
                                   components=[],
                                   dimsRelativeToMax=[],
                                   groups=[]):
        """
        Read solution structure for node fields
        """
        all_iterations, MED_field_name = self._extract_name_and_sequence(fieldName)
        iteration, order = next((a, b) for (a, b, c) in all_iterations if math.isclose(c, self.timeIt))
        
        # read the field under the form of a MEDFileField1TS
        mf_field = ML.MEDFileField1TS(self.fileName, MED_field_name, iteration, order)
        mfMeshName = mf_field.getMeshName()
        mf_mesh = ML.MEDFileUMesh.New(self.fileName, mfMeshName)
        solutionStructure = MEDAsterSolutionStructure(MEDMesh(mf_mesh), "node")

        
        #mc_field_bg = mf_field.getFieldAtTopLevel(ML.ON_NODES, False)
        mc_field_bg = mf_field.getFieldOnMeshAtLevel(ML.ON_NODES, 0, mf_mesh)

        # First, build array of nodes to keep
        extractDef = {}

        nodeIdsGlobalArray = None
        if groups:
            nodeIdsGlobalArray = mf_mesh.getNodeGroupsArr(groups, False)
            extractDef[1] = nodeIdsGlobalArray
        
        # --- Loop over relative dimensions
        nonEmptyLevels = list(mf_mesh.getNonEmptyLevels())
        includedLevels = reversed(sorted(dimsRelativeToMax)) if dimsRelativeToMax else nonEmptyLevels
        
        walkedLevels = reversed(sorted(list(set(nonEmptyLevels).intersection(includedLevels))))

        for level in walkedLevels:
            extractDef[level] = ml.DataArrayInt.New(list(range(mf_mesh.getNumberOfCellsAtLevel(level))))

        finalNodeIdsGlobalArray = mf_mesh.deduceNodeSubPartFromCellSubPart(extractDef)
        restricted_mf_mesh = mf_mesh.extractPart(extractDef)
        mc_restricted_mesh = restricted_mf_mesh.getMeshAtLevel(0, False)
        
        # Create MEDCouplingField from scratch, based on user doc
        fieldOnNodes=ml.MEDCouplingFieldDouble(ml.ON_NODES, ml.ONE_TIME)
        fieldOnNodes.setName(mc_field_bg.getName())
        fieldOnNodes.setMesh(mc_restricted_mesh)
        fieldOnNodes.setTime(self.timeIt, iteration, order)
        array=ml.DataArrayDouble()
        array.alloc(fieldOnNodes.getMesh().getNumberOfNodes(), mc_field_bg.getNumberOfComponents()) # Implicitly fieldOnNodes will be a 1 component field.
        array.fillWithValue(0.)
        array.setInfoOnComponents(mc_field_bg.getArray().getInfoOnComponents())

        fieldOnNodes.setArray(array)

        fieldOnNodes.checkConsistencyLight()

        if components:
            list_of_compos = fieldOnNodes.getArray().getInfoOnComponents()
            compos_num_to_select = [list_of_compos.index(c) for c in components]
            fieldOnNodes = fieldOnNodes.keepSelectedComponents(compos_num_to_select)
    
        internalStorage = {}

        # Put this array at level 0, and a global sample field
        internalStorage[0] = (fieldOnNodes, finalNodeIdsGlobalArray)
        
        #for level in walkedLevels:
            
        #    tab = {}
        #    tab[1] = extractDef[1]
        #    tab[level] = extractDef[level]
            
        #    nodeIdsArray = mf_mesh.deduceNodeSubPartFromCellSubPart(tab)
        #    restr_mf_mesh = mf_mesh.extractPart(tab)
            
        #    relNodeIds = ml.DataArrayInt(list(filter(lambda x: finalNodeIdsGlobalArray[x] in nodeIdsArray, range(len(finalNodeIdsGlobalArray)))))
            
        #    internalStorage[level] = relNodeIds
        
        solutionStructure.SetInternalStorage(internalStorage)
        return solutionStructure
        