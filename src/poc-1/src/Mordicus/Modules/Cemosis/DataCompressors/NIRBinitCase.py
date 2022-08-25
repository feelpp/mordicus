import os
import os.path as osp

import subprocess
import feelpp 
import sys, os
import feelpp
import feelpp.mor as mor
from feelpp.toolboxes.heat import *
import feelpp.interpolation as fi
import json5 as json



def assembleToolbox(tb, mu):

    for i in range(0,mu.size()):
        tb.addParameterInModelProperties(mu.parameterName(i), mu(i))
    tb.updateParameterValues()



def createInterpolator(tbCoarse, tbFine):
    """Create an interpolator between two toolboxes
    
    Args:
        tbCorase (Toolbox): coarse toolbox
        tbFine (Toolbox): fine toolbox
    """
    Vh_coarse = tbCoarse.spaceTemperature()
    Vh_fine = tbFine.spaceTemperature()
    interpolator = fi.interpolator(domain = Vh_coarse, image = Vh_fine, range = tbCoarse.rangeMeshElements())
    return interpolator



def initproblem(numberOfInitSnapshot, tbFine, tbCoarse, Dmu):
        
    """ 
    ----------------------------------------------------
         generate snapshots in case POD method 
    ----------------------------------------------------
    tbFine : toolbox for fine mesh (initialized) 
    tbCoarse : toolbox for coarse mesh (initialized)
    Dmu : Space parameters 
    numberOfSnapshot : the number of snapshot for initialization 

    """ 
    mu = Dmu.element()


    print("-----------------------------------")
    print("   Get Initialized Snapshots       ")
    print("-----------------------------------")

    fineSnapList = []
    coarseSnapList = []

    for param in range(numberOfInitSnapshot):

        dicparam = dict([ (mu.parameterName(i), mu(i)/float(param+1)) for i in range(mu.size())])

        mu.setParameters(dicparam)

        if feelpp.Environment.isMasterRank():
            print(f"Running simulation with mu = {mu}")

        assembleToolbox(tbCoarse, mu)
        assembleToolbox(tbFine, mu)

        tbFine.solve()
        tbCoarse.solve()

        fineSnapList.append(tbFine.fieldTemperature())
        coarseSnapList.append(tbCoarse.fieldTemperature())

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

def loadModel(model_path):
    """Load the model from given modele path

    Args:
        model_path (str): path to the model file (JSON)

    Returns:
        json: model loaded
    """
    f = open(model_path, "r")
    model = json.load(f)
    f.close()
    return model

def loadParameterSpace(model_path):

    crb_model_properties = mor.CRBModelProperties("", feelpp.Environment.worldCommPtr(), "")
    crb_model_properties.setup(model_path)
    Dmu = feelpp.mor._mor.ParameterSpace.New(crb_model_properties.parameters(), feelpp.Environment.worldCommPtr())
    return Dmu


def setToolbox(h, geo_path, model, order=2):

    # load meshes
    mesh_ = feelpp.mesh(dim=2, realdim=2)
    mesh = feelpp.load(mesh_, geo_path, h)

    # set mesh and model properties
    tb = heat(dim=2, order=order)
    tb.setMesh(mesh)
    tb.setModelProperties(model)

    tb.init()

    return tb

def SolveFpp(toolBox, mu):
        
    """ 
    ----------------------------------------------------
         generate snapshots in case POD method 
    ----------------------------------------------------
    tbFine : toolbox for fine mesh (initialized) 
    tbCoarse : toolbox for coarse mesh (initialized)
    Dmu : Space parameters 
    numberOfSnapshot : the number of snapshot for initialization 

    """ 

    assembleToolbox(toolBox, mu)

    toolBox.solve()

    return toolBox.fieldTemperature()


