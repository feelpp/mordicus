# -*- coding: utf-8 -*-
from Mordicus.Core.Containers.Meshes.MeshBase import MeshBase
from Mordicus.Core.Containers.CollectionProblemData import CollectionProblemData

import numpy as np 

import pdb


def selection( basis: np.ndarray ) -> list:
    """Function to perform DEIM like selection of unknown to keep for the RID construction. Unknown can be nodal or integrated values
    
    Arguments:
        basis {np.ndarray} -- The full reduced order basis
    
    Returns:
        list -- the unknown rank to keep
    """
    
    n_dof, n_modes = basis.shape
    rid_ddl = []
    V = basis.copy()
    rk_max = np.argmax( np.abs(V[:,0]) )
    rid_ddl.append( rk_max )
    norm0 = abs(V[rk_max,0])
    V[:,0] /= norm0
    V[rk_max, 0] = 0.
    j_cum = [0]

    for m in range(1,n_modes):
        v_red = V[np.ix_(rid_ddl, [m,])]
        u_red = basis[np.ix_(rid_ddl, j_cum)]
        v_tmp = u_red.T.dot( v_red )
        utu = u_red.T.dot(u_red)
        try:
            sol = np.linalg.solve( utu, v_tmp)
        except np.linalg.LinAlgError:
            print("Becarefull the reduce integration domain construction seems badly conditionned")
            continue
        x = np.zeros((V.shape[1],1))
        x[:sol.shape[0], [0,]] = sol
        q = -1.*V.dot(x) + 1.*V[:,[m]]
        rk_max = np.argmax( np.abs(q) )
        q /= np.abs(q[rk_max])
        rid_ddl.append(rk_max)
        j_cum.append( m )
    return rid_ddl

def BuildReducedIntegrationOperator(collectionProblemData: CollectionProblemData, mesh: MeshBase, extend=0, listNameDualVarOutput = []):
    """[summary]
    
    Arguments:
        collectionProblemData {CollectionProblemData} -- [description]
        mesh {MeshBase} -- [description]
    
    Keyword Arguments:
        extend {int} -- the number of additional layers to keep (default: {0})
        listNameDualVarOutput {list} -- the list of dual variable to use in addition to nodal ones (default: {[]})
    """

    print("Compute Reduced Integration Domain ... ")
    
    ## Step 1. Select dofs
    reducedOrderBasis = collectionProblemData.GetReducedOrderBasis("U").transpose() 
    rid_ddl = selection(reducedOrderBasis)
    print("DOFs selection done")

    ## Step 2. Select dual variable 
    rid_dual = {}
    
    for name in listNameDualVarOutput:
        reducedOrderBasis = collectionProblemData.GetReducedOrderBasis(name).transpose()
        rid_dual[name] = selection(reducedOrderBasis)

    
    nn = mesh.GetNumberOfNodes()
    selected_nodes = set([ dof % nn for dof in rid_ddl ])
    print("Identify the associated Reduced Integration Domain")
    ## Build reduced mesh 
    elem_to_keep = []

    for node_rk in selected_nodes:
        elem_to_keep += mesh.GetElemAttach(node_rk)

    ## Integration point to element
    for key, value in rid_dual.items():
        nb_comp = collectionProblemData.GetSolutionsNumberOfComponents(key)
        selected_ip =set([ int(ip/nb_comp) for ip in value ])
        elem_to_keep += [ mesh.GetElemContaining( ip_rank ) for ip_rank in selected_ip ]

    elem_to_keep = set(elem_to_keep)
    for _ in range( extend ):
        dirty_list = []
        for elem in elem_to_keep: 
            for node in mesh.GetElement( elem ):
                dirty_list += mesh.GetElemAttach(node) 
        
        new_elems = set(dirty_list) - elem_to_keep
        print(f"{len(new_elems)} elements added in the RID")

        elem_to_keep = set( list(elem_to_keep) + list(new_elems) )


    operatorCompressionData = {}
    operatorCompressionData["dofs"] = rid_ddl
    operatorCompressionData["rid"] = elem_to_keep
    collectionProblemData.SetOperatorCompressionData( operatorCompressionData )

    