import sys

import feelpp
from Mordicus.Core.Helpers import FolderHandler as FH
from Mordicus.Core.Containers import CollectionProblemData as CPD
from Mordicus.Modules.Cemosis.IO import FeelppMeshReader as FMR
from Mordicus.Modules.Cemosis.DataCompressors import EIMGreedy as EG

from feelpp.toolboxes.heat import toolboxes_options, heat
from feelpp.mor import makeToolboxMorOptions, ParameterSpace

def test():
    
    folderHandler = FH.FolderHandler(__file__)
    folder = folderHandler.scriptFolder+"/opusheat/"

    o = toolboxes_options("heat")
    o.add(makeToolboxMorOptions())
    e = feelpp.Environment(sys.argv,config=feelpp.globalRepository("mordicus"),opts=o)

    configFileName = folder+"opusheat-heat.cfg"
    feelpp.Environment.setConfigFile(configFileName)

    meshFileName = folder+"opusheat.geo"
    print(meshFileName)
    meshReader = FMR.FeelppMeshReader(meshFileName)
    mesh = meshReader.ReadMesh()
    print("Mesh defined in " + meshFileName + " has been read")
    
    heatBox = heat(dim=2,order=1)
    heatBox.setMesh(mesh.GetInternalStorage())
    heatBox.init()
    def assembleDEIM(mu):
        for i in range(0,mu.size()):
            heatBox.addParameterInModelProperties(mu.parameterName(i),mu(i))
        heatBox.updateParameterValues()
        return heatBox.assembleRhs()

    def assembleMDEIM(mu):
        for i in range(0,mu.size()):
            heatBox.addParameterInModelProperties(mu.parameterName(i),mu(i))
        heatBox.updateParameterValues()
        return heatBox.assembleMatrix()

    mp = heatBox.modelProperties().parameters()
    Dmu = ParameterSpace.New(mp, e.worldCommPtr())
    parameter_names = Dmu.parameterNames()
    parameter_types = [float]*len(parameter_names)

    collectionProblemData = CPD.CollectionProblemData()
    collectionProblemData.DefineVariabilityAxes(parameter_names,parameter_types)
    collectionProblemData.DefineQuantity("T", "temperature", "K")
    print("CollectionProblemData with " + str(collectionProblemData.GetNumberOfVariabilityAxes()) + " parameters")

    eim_greedy = EG.GreedyEIMReducedBasis("opusheat", collectionProblemData, heatBox.spaceTemperature(), assembleDEIM, assembleMDEIM)
    mesh_DEIM, mesh_MDEIM = eim_greedy.getReducedMeshes()

    heatBoxDEIM=heat(dim=2,order=1)
    heatBoxDEIM.setMesh(mesh_DEIM)
    heatBoxDEIM.init()

    def assembleOnlineDEIM(mu):
        for i in range(0,mu.size()):
            heatBoxDEIM.addParameterInModelProperties(mu.parameterName(i),mu(i))
        heatBoxDEIM.updateParameterValues()
        return heatBoxDEIM.assembleRhs()

    heatBoxMDEIM=heat(dim=2,order=1)
    heatBoxMDEIM.setMesh(mesh_MDEIM)
    heatBoxMDEIM.init()

    def assembleOnlineMDEIM(mu):
        for i in range(0,mu.size()):
            heatBoxMDEIM.addParameterInModelProperties(mu.parameterName(i),mu(i))
        heatBoxMDEIM.updateParameterValues()
        return heatBoxMDEIM.assembleMatrix()

    eim_greedy.setOnlineAssembly(assembleOnlineDEIM, assembleOnlineMDEIM)
    eim_greedy.computeReducedBasis("T")

    print(collectionProblemData.reducedOrderBases)

if __name__ == "__main__":
    test()
