import sys
from feelpp.mor.nirb import nirb 
from feelpp.mor.nirb.utils import WriteVecAppend, init_feelpp_environment, generatedAndSaveSampling

class nirbOfflineFeelpp :
    """
    Class containing a wrapping of nirb offline support from Feel++
    """

    def __init__(self, nbSnap=None, initCoarse=False, **kwargs ):

        self.nirbOffline = nirb.nirbOffline(initCoarse=initCoarse, **kwargs)
        self.doGreedy = kwargs['greedy-generation']
        self.N = nbSnap
        if self.N==None : self.N = kwargs['nbSnapshots'] 

        
    def getReducedBasis(self):
        """Wrapping of nirb reduced basis
        """
        self.nirbOffline.generateOperators(coarse=self.doGreedy)

        if self.doGreedy:
            Xi_train = None 
            _, Xi_train, _ = self.nirbOffline.initProblemGreedy(100, 1e-5, Nmax=self.N, Xi_train=Xi_train, computeCoarse=True, samplingMode="random")
        else:
            Xi_train = self.nirbOffline.initProblem(self.N)
        
        self.nirbOffline.generateReducedBasis()

        self.reducedBasis = self.nirbOffline.reducedBasis 

    def checkconvergence(self,Ns=30, Xi_test=None):
        """Compute convergence error of nirb offline

        Args:
            Ns (int, optional): number of parameter in the samplin test. Defaults to 30.
            Xi_test (list, optional): set of sampling test. Defaults to None.
        """

        return self.nirbOffline.checkConvergence(Ns, Xi_test)

    def checkOrthogonality(self):
        """check L2 orhtonormalization of reduced basis function 
        """
        return self.nirbOffline.checkL2Orthonormalized()

    def saveData(self, RESPATH='./', force=True):
        """save datas generated on the offline step 

        Args:
            RESPATH (str, optional): output dir to save data. Defaults to './'.
        """
        self.nirbOffline.saveData(RESPATH, force=force)


class nirbOnlineFeelpp :
    """Class containing a wrapping of nirb online support from Feel++
    """

    def __init__(self, **kwargs) :

        self.nirbOnline = nirb.nirbOnline(**kwargs)
        self.tbFine = self.nirbOnline.tbFine 
        self.tbCoarse = self.nirbOnline.tbCoarse 

    def loadData(self, RESPATH='./', nbSnap=None):
        """Load data generated from nirb offline step 

        Args:
            RESPATH (str, optional): input directory to load data. Defaults to './'.
            N (int, optional): number of basis function to load. Defaults to None.
        """
        err = self.nirbOnline.loadData(path=RESPATH, nbSnap=nbSnap)
        assert err == 0, f"Error while loading data "
        return err 

    def getOnlineSol(self, mu):
        """get nirb online solution 

        Args:
            mu (parameter): parameter to compute the approximate solution
        """
        return self.nirbOnline.getOnlineSol(mu)
    
    def getInterpSol(self, mu):
        """return the interpolation of coarse FE solution into fine mesh

        Args:
            mu (parameter) : feelpp parameter 
        """

        return self.nirbOnline.getInterpSol(mu) 

    def getToolboxSol(self,mu, toolbox=None):
        """return the FE solution associated to toolbox tb

        Args:
            mu (parameter): feelpp parameter 
            toolbox (feelpp toolbox, optionnal) : feelpp toolbox. DEfaults to None
        """

        if toolbox ==None : 
            tb = self.tbFine
        else :
            tb = toolbox

        return self.nirbOnline.getToolboxSolution(tb, mu)

    # def exportField(self, field, name):
    #     """export field for vizualisation

    #     Args:
    #         field (_type_): _description_
    #         name (_type_): _description_
    #     """



    

    