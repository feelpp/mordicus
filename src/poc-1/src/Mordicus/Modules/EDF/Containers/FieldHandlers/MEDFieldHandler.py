import medcoupling as mc
import sympy
import numpy as np

from Mordicus.Core.Containers.FieldHandlers.FieldHandlerBase import FieldHandlerBase

def safe_clone(mc_field):
    """
    Safely initializaing field with the same structure as sample field mc_clone
    """
    template = mc.MEDCouplingFieldTemplate(mc_field)
    array = mc.DataArrayDouble.New()
    array.alloc(mc_field.getNumberOfTuples(), mc_field.getNumberOfComponents())
    array.setInfoOnComponents(mc_field.getArray().getInfoOnComponents())
    array.fillWithZero()
    field = mc.MEDCouplingFieldDouble.New(template)
    field.setArray(array)
    return field

class MEDFieldHandler(FieldHandlerBase):
    """
    Field operations implemented with MEDCouplingFIeldDouble
    """

    def ConvertToLocalField(self, solutionStructure, vector):
        """
        Parameters
        ----------
        solutionStructure : MEDAsterSolutionStructure
            Structure instance as defined by mordicus datamodel
        vector : nparray
            numpy array of solution to convert

        Returns
        -------
        dict(int:MEDCouplingFieldDouble)
            field in the local Type
        """
        if solutionStructure.discr in ("node", ):
            fieldInstanceNode, _ = solutionStructure.GetInternalStorage()[0]
            f = safe_clone(fieldInstanceNode)
            f.setName("convert_" + f.getName())
            f.getArray().setValues(list(vector.flatten()), f.getNumberOfTuples(), f.getNumberOfComponents())
            return {1: f}

        if solutionStructure.discr in ("gauss", "cell"):
            fieldInstances = solutionStructure.GetInternalStorage()
            
            res = {}
            offset = 0

            for level, (fieldInstance, _) in fieldInstances.items():
                f = safe_clone(fieldInstance)
                f.setName("convert_" + f.getName())
                offset_new = f.getNumberOfValues()
                f.getArray().setValues(list(vector.flatten()[offset:offset_new]), f.getNumberOfTuples(), f.getNumberOfComponents())
                offset_new = offset
                res[level] = f
            return res            

    def doublContractedProduct(self, localSigmaField, localEpsilonField):
        """
        Parameters
        ----------
        localSigmaField : dict(int:MEDCouplingFieldDouble)
            first field (symmetric 3x3 matrix)
        localEpsilonField : dict(int:MEDCouplingFieldDouble)
            second field (symmetric 3x3 matrix)

        Returns
        -------
        dict(int:MEDCouplingFieldDouble)
            field with 1 component, result of the doubly contracted product
        """
        res = {}
        for level, sigma in localSigmaField.items():
            epsilon = localEpsilonField[level]
            mult = safe_clone(sigma)
            
            mult.fillFromAnalytic(sigma.getNumberOfComponents(), "1.*IVec+1.*JVec+1.*KVec+2.*LVec+2.*MVec+2.*NVec")
            mult.checkConsistencyLight()
    
            sigma2 = mc.MEDCouplingFieldDouble.MultiplyFields(mult, sigma)
    
            sigma2_array = sigma2.getArray()
            epsilon_array = epsilon.getArray()
    
            template = mc.MEDCouplingFieldTemplate(sigma)
            array = mc.DataArrayDouble.New()
            array.alloc(sigma.getNumberOfTuples())
            array.fillWithZero()
            dc_prod = np.sum(np.multiply(sigma2_array.toNumPyArray(), epsilon_array.toNumPyArray()), axis=1)
            array.setValues(list(dc_prod), sigma.getNumberOfTuples(), 1)
            
            field = mc.MEDCouplingFieldDouble.New(template)
    
            field.setArray(array)
            res[level] = field
    
        return res

    def integral(self, localField, componentNumber):
        """
        Parameters
        ----------
        localField : dict(int:MEDCouplingFieldDouble)
            field to integrate over its whole domain Omega
        componentNumber : int
            number of the component number to integrate
        
        Returns
        -------
        double : integral over Omega of field(componentNumber)
        """
        sumAll = np.double(0.0)
        for _, field in localField.items():
            sumAll = sumAll + field.integral(componentNumber, True)
        return sumAll

    def ConvertFromLocalField(self, localField):
        """
        Parameters
        ----------
        localField : dict(int: MEDCouplingFieldDouble)

        Returns
        -------
        np.array:
            numpy array of field values

        Note: similarities with MEDSolutionReader.ReadSnapshotComponent
        """
        vector = None
        for _, mc_field in localField.items():
            if vector is not None:
                vector = np.concatenate((vector, mc_field.getArray().toNumPyArray().flatten()), axis=0)
            if vector is None:
                vector = mc_field.getArray().toNumPyArray().flatten()
                
        return vector
    
    def symetricGradient(self, localField, solutionStructureGauss, solutionStructureNode):
        """
        Parameters
        ----------
        localField : dict{1:MEDCouplingFieldDouble}
            field of nodes for which the gradient should be computed. That field lives on a restricted mesh.
        solutionStructureGauss : MEDAsterSolutionStructure
            solution structure for Gauss fields
        solutionStructureNode : MEDAsterSolutionStructure
            solution structure for node fields
        
        Returns
        -------
        gradients : dict
            relative level as key and MEDCouplingFIeldDouble on gauss points as value
        """
        import numpy.linalg
        localFieldU = localField[1]
        sampleFieldNode, nodeIdsGlobalArray = solutionStructureNode.GetInternalStorage()[0]
        
        fieldInstances = solutionStructureGauss.GetInternalStorage()

        gradients = {}
        for level, (fieldInstance, _) in fieldInstances.items():
            meshRestrOnElems = fieldInstance.getMesh()

            # Create MEDCouplingField from scratch, based on user doc
            fieldOnNodes=mc.MEDCouplingFieldDouble(mc.ON_NODES, mc.ONE_TIME)
            fieldOnNodes.setName(sampleFieldNode.getName())
            fieldOnNodes.setMesh(meshRestrOnElems)
            fieldOnNodes.setTime(0.0, 0, 0)
            array=mc.DataArrayDouble()
            array.alloc(meshRestrOnElems.getNumberOfNodes(), sampleFieldNode.getNumberOfComponents()) # Implicitly fieldOnNodes will be a 1 component field.
            array.fillWithValue(0.)
            fieldOnNodes.setArray(array)
            fieldOnNodes.checkConsistencyLight()
            
            # fill with values from localFieldU
            array[nodeIdsGlobalArray] = localFieldU.getArray().deepCopy()

            field_array = array.toNumPyArray()
            coor_array = meshRestrOnElems.getCoords().toNumPyArray()
    
            gradients[level] = safe_clone(fieldInstance)
            res_array = gradients[level].getArray()
          
            dN = self._derivativesOfShapeFunction(fieldInstance)
            
            # The following is clearly not optimal (python loop)
            for cellId in range(meshRestrOnElems.getNumberOfCells()):
                
                # Get ordered connectivity of element            
                nodesIds = meshRestrOnElems.getNodeIdsOfCell(cellId)
                # #Identical to :
                # tab_conn = restrMesh.getNodalConnectivity()
                # nodesIds = tab_conn[21*cellId+1:21*(cellId+1)]
                
                # #We should have:
                assert list(fieldOnNodes.computeTupleIdsToSelectFromCellIds(cellId).toNumPyArray()) == sorted(nodesIds)
                
                # Get array of field and displacement coordinates
                arrayU = field_array[nodesIds,:]
                arrayX = coor_array[nodesIds,:]
    
                # Retrieve array of coordinates
                dF = np.tensordot(dN, arrayX, axes=([0],[0]))
                inv_dF = np.zeros((3,3))
                
                # Construct numpy array of inverse matrices
                for igp in range(27):
                    dFg = dF[:,igp,:]
    
                    inv_dF = numpy.linalg.inv(dFg)
                    gradUg = np.tensordot(arrayU, np.tensordot(dN[:,:,igp], inv_dF, axes=([1],[1])), axes=([0],[0]))
                    
                    # Fill in Gauss field with these values
                    res_array[27*cellId+igp,0] = gradUg[0,0]
                    res_array[27*cellId+igp,1] = gradUg[1,1]
                    res_array[27*cellId+igp,2] = gradUg[2,2]
                    res_array[27*cellId+igp,3] = (gradUg[0,1] + gradUg[1,0])/2.
                    res_array[27*cellId+igp,4] = (gradUg[0,2] + gradUg[2,0])/2.
                    res_array[27*cellId+igp,5] = (gradUg[1,2] + gradUg[2,1])/2.
            
        return gradients

    def _derivativesOfShapeFunction(self, fieldInstance):
        """
        Parameters
        ----------
        fieldInstance : MEDCouplingFieldDouble
            used to get the reference coordinates of Gauss points
        
        Returns
        -------
        nparray
            res[i,j,k] = \partial N_i / \partial a_j (x_k ), x_k is location of the k-th Gauss point
            
        For now, works only with the HEXA_20 element
        """
        # For now, in this implementation, only one Gauss discretization, has to be HEXA_20
        assert fieldInstance.getDiscretization().getNbOfGaussLocalization() == 1
        assert fieldInstance.getDiscretization().getGaussLocalization(0).getType() == mc.NORM_HEXA20

        # Define symbolic shape functions and their derivatives
        import sympy as sp
        
        a1, a2, a3 = sp.symbols("a1 a2 a3")
        funValue = [None]*20
        funValue[0] = 0.125*(1.0 - a1)*(1.0 - a2)*(1.0 - a3)*(-2.0 - a1 - a2 - a3)
        funValue[1] = 0.125*(1.0 + a1)*(1.0 - a2)*(1.0 - a3)*(-2.0 + a1 - a2 - a3)
        funValue[2] = 0.125*(1.0 + a1)*(1.0 + a2)*(1.0 - a3)*(-2.0 + a1 + a2 - a3)
        funValue[3] = 0.125*(1.0 - a1)*(1.0 + a2)*(1.0 - a3)*(-2.0 - a1 + a2 - a3)
        funValue[4] = 0.125*(1.0 - a1)*(1.0 - a2)*(1.0 + a3)*(-2.0 - a1 - a2 + a3)
        funValue[5] = 0.125*(1.0 + a1)*(1.0 - a2)*(1.0 + a3)*(-2.0 + a1 - a2 + a3)
        funValue[6] = 0.125*(1.0 + a1)*(1.0 + a2)*(1.0 + a3)*(-2.0 + a1 + a2 + a3)
        funValue[7] = 0.125*(1.0 - a1)*(1.0 + a2)*(1.0 + a3)*(-2.0 - a1 + a2 + a3)
  
        funValue[8] = 0.25*(1.0 - a1*a1)*(1.0 - a2)*(1.0 - a3)
        funValue[9] = 0.25*(1.0 - a2*a2)*(1.0 + a1)*(1.0 - a3)
        funValue[10] = 0.25*(1.0 - a1*a1)*(1.0 + a2)*(1.0 - a3)
        funValue[11] = 0.25*(1.0 - a2*a2)*(1.0 - a1)*(1.0 - a3)

        funValue[12] = 0.25*(1.0 - a1*a1)*(1.0 - a2)*(1.0 + a3)
        funValue[13] = 0.25*(1.0 - a2*a2)*(1.0 + a1)*(1.0 + a3)
        funValue[14] = 0.25*(1.0 - a1*a1)*(1.0 + a2)*(1.0 + a3)
        funValue[15] = 0.25*(1.0 - a2*a2)*(1.0 - a1)*(1.0 + a3)

        funValue[16] = 0.25*(1.0 - a3*a3)*(1.0 - a1)*(1.0 - a2)
        funValue[17] = 0.25*(1.0 - a3*a3)*(1.0 + a1)*(1.0 - a2)
        funValue[18] = 0.25*(1.0 - a3*a3)*(1.0 + a1)*(1.0 + a2)
        funValue[19] = 0.25*(1.0 - a3*a3)*(1.0 - a1)*(1.0 + a2)
        
        diffValue = [[None]*3 for i in range(20)]
        for i in range(20):
            diffValue[i][0] = sp.diff(funValue[i], a1)
            diffValue[i][1] = sp.diff(funValue[i], a2)
            diffValue[i][2] = sp.diff(funValue[i], a3)
        
        # Get reference coordinates of Gauss points
        tup_coor = fieldInstance.getDiscretization().getGaussLocalization(0).getGaussCoords()
        
        # Evaluate symbolic derivatives there
        np_coor = np.array(tup_coor).reshape((-1, 3))
        res = np.zeros((20, 3, 27))
        
        for i in range(20):
            for j in range(3):
                for k in range(27):
                    res[i,j,k] = diffValue[i][j].evalf(16, subs={a1:np_coor[k,0], a2:np_coor[k,1], a3:np_coor[k,2]}, chop=True)
        return res

    def gaussPointsCoordinates(self, solutionStructureGauss):
        """
        Get the Gauss point coordinate a family of solutions relies on
        
        Arguments
        ---------
        solutionStructureGauss
            a solution structure with discretization on Gauss points (any number of components)
         
        Returns:
        -------
        ndarray
            numpy array of Gauss points coordinates for the given solutionStructureGauss
        """
        coords = None
        solutionStructure = solutionStructureGauss.GetInternalStorage()
        for _, (sample_field, _) in solutionStructure.items():
            if coords is not None:
                coords = np.concatenate((coords, sample_field.getLocalizationOfDiscr().toNumPyArray()), axis=0)
            if coords is None:
                coords = sample_field.getLocalizationOfDiscr().toNumPyArray()
        return coords

    def getVolume(self, solutionStructureGauss):
        """
        Compute volume getting Gauss points from a sample field
        
        Arguments
        ---------
        solutionStructureGauss
            a solution structure with discretization on Gauss points (any number of components)
            
        Returns
        -------
        double
            volume of the domain the family of solutions is defined on
        """
        solutionStructure = solutionStructureGauss.GetInternalStorage()

        volume = np.double(0.0)
        for _, (sample_field, _) in solutionStructure.items():
        # deep copy field
            f = safe_clone(sample_field)
            
            # set number of components to 1
            f.changeNbOfComponents(1)
            
            # fill and compute integral
            f.fillFromAnalytic(1, "1")
            volume = volume + f.integral(0, True) 

        return volume

        

        