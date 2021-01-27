import medcoupling as mc
import sympy
import numpy as np

from Mordicus.Core.Containers.FieldHandlers.FieldHandlerBase import FieldHandlerBase

class MEDFieldHandler(FieldHandlerBase):
    """
    Field operations implemented with MEDCouplingFIeldDouble
    """

    def ConvertToLocalField(self, fieldInstance, vector):
        """
        Parameters
        ----------
        structure : Structure
            Structure instance as defined by mordicus datamodel
        vector : nparray
            numpy array of solution to convert

        Returns
        -------
        MEDCouplingFieldDouble
            field in the local Type
        """
        f = fieldInstance.clone(True)
        f.setName("convert_" + f.getName())
        array_shape = (f.getNumberOfTuples(), f.getNumberOfComponents())
        f.setArray(mc.DataArrayDouble(vector.reshape(array_shape)))
        return f
    
    def doublyContractedProduct(self, sigma, epsilon):
        """
        Parameters
        ----------
        sigma : MEDCouplingFieldDouble
            first field (symmetric 3x3 matrix)
        epsilon : MEDCouplingFieldDouble
            second field (symmetric 3x3 matrix)

        Returns
        -------
        doublyContractedProduct : MEDCouplingFieldDouble
            field with 1 component, result of the doubly contracted product
        """
        mult = sigma.clone(True)
        mult.fillFromAnalytic(7, "1.*IVec+1.*JVec+1.*KVec+2.*LVec+2.*MVec+2.*NVec+0.*OVec")
        sigma2 = mc.MEDCouplingFieldDouble.MultiplyFields(mult, sigma)
        return mc.MEDCouplingFieldDouble.DotFields(sigma2, epsilon)

    def integral(self, field, componentNumber):
        """
        Parameters
        ----------
        field : MEDCouplingFieldDouble
            field to integrate over its whole domain Omega
        componentNumber : int
            number of the component number to integrate
        
        Returns
        -------
        double : integral over Omega of field(componentNumber)
        """
        return field.integral(componentNumber, True)

    def ConvertFromLocalField(self, field):
        """
        Parameters
        ----------
        field : MEDCouplingFieldDouble

        Returns
        -------
        np.array:
            numpy array of field values

        Note: similarities with MEDSolutionReader.ReadSnapshotComponent
        """
        data_array_double = field.getArray()
        # TODO: discuss the opportunity of adding ".flatten()" here
        return data_array_double.toNumPyArray()
    
    def symetricGradient(self, field, fieldInstanceGauss):
        """
        Parameters
        ----------
        field : MEDCouplingFieldDouble
            Should have a discretization ON_NODES
        
        Returns
        -------
        field : MEDCouplingFieldDouble
        """
        import numpy.linalg
        restrMesh = field.getMesh()
        field_array = field.getArray().toNumPyArray()
        coor_array = restrMesh.getCoords().toNumPyArray()
        res = fieldInstanceGauss.clone(True)
        res_array = res.getArray()
        res_array[:,:] = 0
        
        dN = self._derivativesOfShapeFunction(fieldInstanceGauss)
        
        # The following is clearly not optimal (python loop)
        for cellId in range(restrMesh.getNumberOfCells()):
            
            # Get ordered connectivity of element            
            nodesIds = restrMesh.getNodeIdsOfCell(cellId)
            # #Identical to :
            # tab_conn = restrMesh.getNodalConnectivity()
            # nodesIds = tab_conn[21*cellId+1:21*(cellId+1)]
            
            # #We should have:
            assert list(field.computeTupleIdsToSelectFromCellIds(cellId).toNumPyArray()) == sorted(nodesIds)
            
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
            
        return res

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
        