import numpy as np

class GreedyEIMReducedBasis:
    def __init__(self, name, collectionProblemData, space, assembleDEIM, assembleMDEIM):
        from feelpp.mor import toolboxmor_2d
        self.name = name
        self.collectionProblemData = collectionProblemData
        self.model = toolboxmor_2d(name)
        self.model.setFunctionSpaces(Vh=space)
        self.model.setAssembleDEIM(fct=assembleDEIM)
        self.model.setAssembleMDEIM(fct=assembleMDEIM)
        self.model.initModel()
    
    def getReducedMeshes(self):
        return (self.model.getDEIMReducedMesh(), self.model.getMDEIMReducedMesh())

    def setOnlineAssembly(self, assembleOnlineDEIM, assembleOnlineMDEIM):
        self.model.setOnlineAssembleDEIM(assembleOnlineDEIM)
        self.model.setOnlineAssembleMDEIM(assembleOnlineMDEIM)
        self.model.postInitModel()
        self.model.setInitialized(True)

    def computeReducedBasis(self, solutionName):
        from feelpp.mor import crbmodel_toolboxmor_2d, crb_toolboxmor_2d

        self.crbmodel = crbmodel_toolboxmor_2d(self.model)
        self.crb = crb_toolboxmor_2d(self.crbmodel, self.name)
        self.crb.offline()

        rb = self.crb.primalReducedBasis()
        if len(rb) == 0:
            self.collectionProblemData.reducedOrderBases[solutionName] = np.array((0,0))
            return
        N = len(rb)
        ndof = rb[0].functionSpace().nLocalDof()
        self.collectionProblemData.reducedOrderBases[solutionName] = np.zeros((N,ndof))
        for i, u in enumerate(rb):
            self.collectionProblemData.reducedOrderBases[solutionName][i,:] = rb[i].to_petsc().vec()[:]
