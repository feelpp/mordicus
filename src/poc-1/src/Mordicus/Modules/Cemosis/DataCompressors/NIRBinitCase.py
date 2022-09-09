import os
import os.path as osp

import subprocess
import feelpp 
import sys, os
import feelpp
import feelpp.mor as mor
import feelpp.toolboxes.heat as heat 
import feelpp.toolboxes.fluid as fluid
import feelpp.interpolation as fi
import json5 as json
from feelpp.mor.nirb.nirb import * 

# nirb_dir = "/data/home/elarif/devel/feelpp/python/pyfeelpp-toolboxes/feelpp/toolboxes/nirb/"
# sys.path.append(nirb_dir)
# from feelpp.mor.
# from nirb import *

def initproblem(numberOfInitSnapshot, Dmu, tbFine, tbCoarse=None, type_tb='heat', samplingMode="log-random"):
        
    """ 
    ----------------------------------------------------
         generate snapshots in case POD method 
    ----------------------------------------------------
    tbFine : toolbox for fine mesh (initialized) 
    tbCoarse : toolbox for coarse mesh (initialized) if Rectification 
    ListParam : list of Space parameters (to be done)
    numberOfSnapshot : the number of snapshot for initialization 
    samplingMode : sampling mode for parameter space random, log-random, log-equidistribute, equidistribute

    """ 
    mu = Dmu.element()

    print("-----------------------------------")
    print("   Get Initialized Snapshots       ")
    print("-----------------------------------")

    fineSnapList = []
    coarseSnapList = []

    s = Dmu.sampling()
    s.sampling(numberOfInitSnapshot, samplingMode)
    vector_mu = s.getVector()

    if tbCoarse!=None :
        for mu in vector_mu :

            if feelpp.Environment.isMasterRank():
                print(f"Running simulation with mu = {mu}")

            assembleToolbox(tbCoarse, mu)
            assembleToolbox(tbFine, mu)

            tbFine.solve()
            tbCoarse.solve()

            if (type_tb=='fluid') :       
                fineSnapList.append(tbFine.fieldVelocity())
                coarseSnapList.append(tbCoarse.fieldVelocity())
            else :
                fineSnapList.append(tbFine.fieldTemperature())
                coarseSnapList.append(tbCoarse.fieldTemperature())
    else :
        for mu in vector_mu :

            if feelpp.Environment.isMasterRank():
                print(f"Running simulation with mu = {mu}")

            assembleToolbox(tbFine, mu)

            tbFine.solve()

            if (type_tb=='fluid') :       
                fineSnapList.append(tbFine.fieldVelocity())
            else :
                fineSnapList.append(tbFine.fieldTemperature())

    #     exportFine = feelpp.exporter(mesh=fineMesh, name="Snapshot")
    #     exportFine.addScalar(f"mu{param}", mu(1))
    #     # exportFine.step()
    #     exportFine.addP2c(f"Temperature{param}", tbFine.fieldTemperature())

    #     exportCoarse = feelpp.exporter(mesh=coarseMesh, name="SnapshotH")
    #     exportCoarse.addScalar(f"mu{param}", mu(1))
    #     # exportFine.step(param)
    #     exportCoarse.addP2c(f"Temperature{param}", tbCoarse.fieldTemperature())
    
    # exportCoarse.save()
    # exportFine.save()

        #tbFine.printAndSaveInfo()
        #tbFine.exportResults(time=2) # export the results for paraview 
        #tbCoarse.exportResults() # export the results for paraview 
    
    print("Number of Snapshots computed = ", len(fineSnapList))
    print("Initialize Snapshots DONE ")

    return fineSnapList, coarseSnapList

def SolveFpp(toolBox, mu, type_tb='heat'):
        
    """ 
    ----------------------------------------------------
        Given a parameter mu, get Finite element solution 
                associated to this parameter 
    ----------------------------------------------------
    toolBox : toolbox (initialized) 
    mu : crb_parameter 
    type_tb : type of toolbox ('heat' of 'fluid')
    """ 

    assembleToolbox(toolBox, mu)

    toolBox.solve()

    if (type_tb=='fluid') :       
        return toolBox.fieldVelocity()
    elif (type_tb=='heat') :
        return toolBox.fieldTemperature()
    else :
        raise ValueError("type_tb must be 'heat' or 'fluid'")
        


