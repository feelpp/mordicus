# -*- coding: utf-8 -*-

import os, sys
from mpi4py import MPI
if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
import numpy as np

from mpi4py import MPI
from pathlib import Path

from Mordicus.Core.IO.InputReaderBase import InputReaderBase
from BasicTools.IO import ZebulonIO as ZIO


knownLoadingTags = ["pressure", "centrifugal", "temperature", "radiation", "convection_heat_flux"]
knownProblemTypes = ["mechanical", "thermal_transient"]
solutionNames = {"mechanical":"U", "thermal_transient":"T"}


def ReadInputTimeSequence(inputFileName):
    """
    Functional API

    Reads the time sequence from the Z-set input file "inputFileName" (.inp) (may be different from the ones defined in the solution file if the solver chose to solve at additional time steps)

    Parameters
    ----------
    inputFileName : str
        Z-set input file

    Returns
    -------
    np.ndarray
        of size (numberOfSnapshots,)
    """
    reader = ZsetInputReader(inputFileName=inputFileName)
    return reader.ReadInputTimeSequence()


def ConstructLoadingsList(inputFileName, loadingTags = None):
    """
    Constructs the loadings defined in the Z-set input file "inputFileName" (.inp)

    Parameters
    ----------
    inputFileName : str
        Z-set input file

    Returns
    -------
    list
        list of loadings, each one having one of the formats defined in Containers.Loadings
    """
    reader = ZsetInputReader(inputFileName=inputFileName)
    return reader.ConstructLoadingsList(loadingTags)


def ConstructConstitutiveLawsList(inputFileName):
    """
    1
    """
    reader = ZsetInputReader(inputFileName=inputFileName)
    return reader.ConstructConstitutiveLawsList()


class ZsetInputReader(InputReaderBase):
    """
    Class containing a reader for Z-set input file

    Attributes
    ----------
    inputFileName : str
        name of the Z-set input file (.inp)
    inputFile : list
        list containing the input file as parsed by BasicTools.IO.ZebulonIO
    """

    def __init__(self, inputFileName = None, string = None, rootpath = None):
        """
        Parameters
        ----------
        inputFileName : str, optional
        """
        super(ZsetInputReader, self).__init__()

        self.inputFileName = inputFileName
        self.string = string

        if inputFileName is None and string is None:# pragma: no cover
            raise("inputFileName and string cannot be both None")

        if inputFileName is not None and string is not None:# pragma: no cover
            raise("inputFileName and string cannot be both specified")

        if string is not None and rootpath is None:# pragma: no cover
            raise("when string is not None, rootpath must be defined")

        if inputFileName is not None:
            assert isinstance(inputFileName, str)
            self.inputFile = ZIO.ReadInp2(fileName = inputFileName)
            self.rootpath = os.path.dirname(self.inputFileName)
        else:
            self.inputFile = ZIO.ReadInp2(string = string, rootpath = rootpath)
            self.rootpath = rootpath

        self.problemType = ZIO.GetProblemType(self.inputFile)
        assert self.problemType in  knownProblemTypes, "problemType "+self.problemType+" must refer be among "+str(knownProblemTypes)




    def ReadInputTimeSequence(self):
        """
        Reads the time sequence form the inputFile using the parser in BasicTools.IO.ZebulonIO
        """

        return ZIO.GetInputTimeSequence(self.inputFile)





    def ConstructInitialCondition(self):


        zSetInitialCondition = ZIO.GetInitDofValues(self.inputFile)

        solutionName = solutionNames[self.problemType]


        from Mordicus.Modules.Safran.Containers.InitialConditions import InitialCondition

        initialCondition = InitialCondition.InitialCondition()

        if zSetInitialCondition[0] == 'uniform':
            dataType = "scalar"
            data = float(zSetInitialCondition[1])

        elif zSetInitialCondition[0] == 'file':  # pragma: no cover
            dataType = "vector"
            data = ZIO.ReadBinaryFile(self.rootpath + os.sep + zSetInitialCondition[1])


        initialCondition.SetDataType(solutionName, dataType)
        initialCondition.SetInitialSnapshot(solutionName, data)

        return initialCondition



    def ConstructLoadingsList(self, loadingTags = None):

        if not loadingTags:
           loadingTags = knownLoadingTags

        inputTimeSequence = self.ReadInputTimeSequence()

        tables = ZIO.GetTables(self.inputFile)
        zSetLoadings = ZIO.GetLoadings(self.inputFile)

        loadings = []
        for key, value in zSetLoadings.items():
            if key in loadingTags:
                for loadList in zSetLoadings[key]:
                    for load in loadList:
                        loadings.append(self.ConstructOneLoading(key, load, tables, inputTimeSequence))
            else:
                print(
                    "Loading '"
                    + key
                    + "' in inputFile but not among : "
                    + str([key for key in loadingTags])
                    + ", not constructed"
                )

        return loadings


    def ConstructOneLoading(self, key, load, tables, inputTimeSequence):
        """
        Constructs one loading from the Zset input file

        Parameters
        ----------
        key : str
            Zset keyword for the loading
        load : list
            list containing the boundary condition data as defined in BasicTools.IO.ZebulonIO
        tables : dict
            list containing the tables data as defined in BasicTools.IO.ZebulonIO

        Returns
        -------
        LoadingBase
            the constructed loading in one of the formats defined in Containers.Loadings
        """

        import collections

        set = load[0]

        if key == "pressure":
            from Mordicus.Modules.Safran.Containers.Loadings import PressureBC

            loading = PressureBC.PressureBC("U", set)

            sequence = tables[load[3]]
            name = load[2]

            coefficients = collections.OrderedDict()
            fieldsMap = collections.OrderedDict()

            coefficients[float(sequence["time"][0])] = sequence["value"][0]
            fieldsMap[sequence["time"][0]] = name

            lastTimeCycleLoading = float(sequence["time"][-1])
            nbeLoadingCycles = max(int(inputTimeSequence[-1]/lastTimeCycleLoading),1)

            #print("lastTimeCycleLoading =", lastTimeCycleLoading)
            #print("nbeLoadingCycles =", nbeLoadingCycles)

            for j in range(nbeLoadingCycles):
                for i, time in enumerate(sequence["time"][1:]):
                    coefficients[float(time) + j*lastTimeCycleLoading] = sequence["value"][i+1]
                    fieldsMap[float(time) + j*lastTimeCycleLoading] = name

            loading.SetCoefficients(coefficients)
            loading.SetFieldsMap(fieldsMap)

            folder = self.rootpath + os.sep

            fileName = UpdateFileName(name)
            fields = {name: ZIO.ReadBinaryFile(folder + fileName)}

            loading.SetFields(fields)

            return loading


        if key == "centrifugal":

            from Mordicus.Modules.Safran.Containers.Loadings import Centrifugal

            loading = Centrifugal.Centrifugal("U", set)

            center = [float(load[1][1:])]
            count = 2
            for string in load[2:]:
                if string[-1] != ")":
                    center.append(float(string))
                    count += 1
                if string[-1] == ")":
                    center.append(float(string[:-1]))
                    count += 1
                    break
            indexRotationAxis = int(load[count][1:])
            count += 1
            centrifugalCoefficient = float(load[count])
            count += 1
            sequence = tables[load[count]]


            rotationVelocity = collections.OrderedDict()

            rotationVelocity[float(sequence["time"][0])] = sequence["value"][0]


            lastTimeCycleLoading = float(sequence["time"][-1])
            nbeLoadingCycles = max(int(inputTimeSequence[-1]/lastTimeCycleLoading),1)


            for j in range(nbeLoadingCycles):
                for i, time in enumerate(sequence["time"][1:]):
                    rotationVelocity[float(time) + j*lastTimeCycleLoading] = sequence["value"][i+1]


            centrifugalDirection = np.array([1.,0.,0.]*(indexRotationAxis==1)+\
                                            [0.,1.,0.]*(indexRotationAxis==2)+\
                                            [0.,0.,1.]*(indexRotationAxis==3))

            loading.SetCenter(center)
            loading.SetDirection(centrifugalDirection)
            loading.SetCoefficient(centrifugalCoefficient)
            loading.SetRotationVelocity(rotationVelocity)


            return loading


        if key == "radiation":
            #cycles not taken into account yet

            from Mordicus.Modules.Safran.Containers.Loadings import Radiation

            loading = Radiation.Radiation("T", set)

            stefanBoltzmannConstant = float(load[1])
            coefficient = float(load[2])
            sequence = tables[load[3]]

            Text = collections.OrderedDict()
            for i, time in enumerate(sequence["time"]):
                Text[float(time)] = coefficient*sequence["value"][i]

            loading.SetStefanBoltzmannConstant(stefanBoltzmannConstant)

            loading.SetText(Text)

            return loading


        if key == "convection_heat_flux":
            #cycles not taken into account yet

            from Mordicus.Modules.Safran.Containers.Loadings import ConvectionHeatFlux

            loading = ConvectionHeatFlux.ConvectionHeatFlux("T", set)

            coefH = float(load[2])
            coefficient = float(load[4])
            sequence = tables[load[5]]

            h = collections.OrderedDict()
            h[sequence["time"][0]]  = coefH
            h[sequence["time"][-1]] = coefH

            Text = collections.OrderedDict()
            for i, time in enumerate(sequence["time"]):
                Text[float(time)] = coefficient*sequence["value"][i]

            loading.SetH(h)
            loading.SetText(Text)

            return loading


        if key == "temperature":



            from Mordicus.Modules.Safran.Containers.Loadings import Temperature

            loading = Temperature.Temperature("U", set)

            fieldsMap = collections.OrderedDict()
            fields = {}
            folder = self.rootpath + os.sep

            if 'base_temperature' in load[1] and 'max_temperature' in load[1]:
                taleName = load[1]['table'][0]
                timeTable = tables[taleName]['time']
                fileTable = np.array(tables[taleName]['value'], dtype = str)

            else:

                for info in load[1].values():
                    if isinstance(info, dict):
                        timeTable = info['timeTable']
                        fileTable = info['fileTable']


            lastTimeCycleLoading = float(timeTable[-1])
            nbeLoadingCycles = max(int(inputTimeSequence[-1]/lastTimeCycleLoading),1)

            fieldsMap[float(timeTable[0])] = fileTable[0]
            for time, file in zip(timeTable, fileTable):
                fieldsMap[time] = file

            for j in range(nbeLoadingCycles):
                for i, time in enumerate(timeTable[1:]):
                    fieldsMap[time + j*lastTimeCycleLoading] = fileTable[i+1]


            if 'base_temperature' in load[1] and 'max_temperature' in load[1]:

                temperatures = [load[1]['base_temperature'], load[1]['max_temperature']]
                nNodes = int(load[1]['rec_size'][0])

                for i, temperature in enumerate(temperatures):
                    if temperature[0] == 'constant':
                        temperatures[i] = float(temperature[1])*np.ones(nNodes)
                    elif temperature[0] == 'file':
                        fileName = UpdateFileName(temperature[1])
                        temperatures[i] = ZIO.ReadBinaryFile(folder+fileName)
                    else:# pragma: no cover
                        raise("temperature bc not valid")

                #here, keys of fields are the coefficient, not the fileName
                for coef in fileTable:
                    if coef not in fields:
                        coefFloat = float(coef)
                        fields[coef] = coefFloat*temperatures[1] + (1-coefFloat)*temperatures[0]

            else:

                for file in fileTable:
                    if file not in fields:
                        fileName = UpdateFileName(file)
                        fields[file] = ZIO.ReadBinaryFile(folder+fileName)


            fieldsMapTimes = np.array(list(fieldsMap.keys()), dtype = float)
            fieldsMapValues = np.array(list(fieldsMap.values()), dtype = str)

            loading.SetFieldsMap(fieldsMapTimes, fieldsMapValues)
            loading.SetFields(fields)

            return loading




    def ConstructConstitutiveLawsList(self):

        materialFiles = ZIO.GetMaterialFiles(self.inputFile)

        constitutiveLawsList = []

        for set, matFile in materialFiles.items():
            constitutiveLawsList.append(self.ConstructOneConstitutiveLaw(matFile, set))

        return constitutiveLawsList



    def ConstructOneConstitutiveLaw(self, materialFileName, set):
        """
        1
        """

        folder = self.rootpath + os.sep


        behavior = ZIO.GetBehavior(folder + materialFileName)


        if self.problemType == "thermal_transient":

            from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ThermalConstitutiveLaw as TCL

            constitutiveLaw = TCL.ThermalConstitutiveLaw(set)

            constitutiveLaw.SetBehavior(behavior)

            data = ZIO.ReadInp2(folder + materialFileName, startingNstar=3)

            conductivityTemp = []
            conductivityVal = []
            for step in ZIO.GetFromInp(data,{'3':['behavior', 'thermal'], '2':['conductivity', 'isotropic']})[0][2:]:
                conductivityTemp.append(float(step[1]))
                conductivityVal.append(float(step[0]))

            constitutiveLaw.SetThermalConductivity(np.array(conductivityTemp), np.array(conductivityVal))

            capacityTemp = []
            capacityVal = []
            for step in ZIO.GetFromInp(data,{'3':['behavior', 'thermal'], '2':['coefficient']})[0][2:]:
                capacityTemp.append(float(step[1]))
                capacityVal.append(float(step[0]))

            constitutiveLaw.SetThermalCapacity(np.array(capacityTemp), np.array(capacityVal))

            return constitutiveLaw


        if self.problemType == "mechanical":


            behavior = ZIO.GetBehavior(folder + materialFileName)
            density = ZIO.GetDensity(folder + materialFileName)

            return ConstructOneMechanicalConstitutiveLaw(folder, materialFileName, behavior, density, set)




def ConstructOneMechanicalConstitutiveLaw(folder, materialFileName, behavior, density = None, set = "ALLELEMENT"):



    if behavior == "gen_evp":

        from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ZmatConstitutiveLaw as ZCL

        constitutiveLaw = ZCL.ZmatConstitutiveLaw(set)

        constitutiveLaw.SetDensity(density)

        constitutiveLaw.SetBehavior(behavior)

        constitutiveLawVariables = {}

        curFolder = os.getcwd()
        os.chdir(folder)

        suffix = UpdateFileName("")

        if "vtkpython" in sys.executable:#pragma: no cover
            pythonExecutable = "pvpython"
            pyumatFolder = "pvpyumat"
        else:
            pythonExecutable = sys.executable
            pyumatFolder = "pyumat"



        code="""
import sys
from Mordicus.Modules.Safran.External."""+pyumatFolder+""" import py3umat as pyumat
import numpy as np

cmname = '"""+materialFileName+"""'

nstatv = 100
ndi = 3
nshr = 3
ntens = ndi+nshr

stress = np.zeros(6)

statev = np.zeros(nstatv)

ddsdde = np.zeros((6,6),dtype=float)

sse = 0.
spd = 0.
scd = 0.

rpl = 0.
ddsddt = np.zeros(ntens)
drplde = np.zeros(ntens)
drpldt = 0.

stran = np.zeros(6)
dstran = np.zeros(6)
r2 = 2


timesim = np.array([0.,0.1])
dtime = 0.1
temperature = 20.
dtemp = 0.
predef = np.zeros(1)
dpred = np.zeros(1)


nprops = 1
props = np.zeros(nprops)
coords = np.zeros(3, dtype= float)
drot  =  np.zeros((3,3), dtype= float)
pnewdt = 1.
celent = 1.
dfgrd0 = np.zeros((3,3), dtype = float)
dfgrd1 = np.zeros((3,3), dtype = float)
noel = -1
npt = -1
kslay = 1
kspt = 1
kstep = np.array([1,1,0,0], dtype=int)
kinc  = 1

ddsddeNew = pyumat.umat(stress=stress,statev=statev,ddsdde=ddsdde,sse=sse,spd=spd,scd=scd,rpl=rpl,ddsddt=ddsddt,drplde=drplde,drpldt=drpldt,stran=stran,dstran=dstran,time=timesim,dtime=dtime,
                temp=temperature,dtemp=dtemp,predef=predef,dpred=dpred,cmname=cmname,ndi=ndi,nshr=nshr,ntens=ntens,nstatv=nstatv,props=props,nprops=nprops,coords=coords,drot=drot,pnewdt=pnewdt,celent=celent,dfgrd0=dfgrd0,
dfgrd1=dfgrd1,noel=noel,npt=npt,kslay=kslay,kspt=kspt,kstep=kstep,kinc=kinc)"""

        import tempfile
        tmpFile = tempfile.gettempdir()+os.sep


        f = open(tmpFile+"materialtest"+suffix+".py","w")
        f.write(code)
        f.close()

        import subprocess
        import signal

        def handler(signum, frame):# pragma: no cover
            raise Exception("end of time")

        signal.signal(signal.SIGALRM, handler)

        out = None
        while out == None:
            try:
                signal.alarm(10)
                out = subprocess.run([pythonExecutable, tmpFile+"materialtest"+suffix+".py"], stdout=subprocess.PIPE).stdout.decode("utf-8")

            except:# pragma: no cover
                True
            signal.alarm(0)

        outlines = out.split(u"\n")

        seplines = []
        for i in range(len(outlines)):
            if "============================================" in outlines[i]:
                seplines.append(i)
            if "done with material file reading" in outlines[i]:
                lastline = i
        outlines = outlines[seplines[-2]:]

        names = ['Flux', 'Grad','var_int','var_aux','Extra Zmat']


        def parser(fname, obj):
                cont = 1
                line = 0
                while line < len(outlines):
                    if fname in outlines[line]:
                        line +=1
                        while any(word in outlines[line].strip() for word in names) == False and len(outlines[line].strip())>0  and outlines[line][0] != "=":
                            if outlines[line][0] != " ":
                                break# pragma: no cover
                            fnames = outlines[line].strip().split()
                            for i in range(len(fnames)):
                                if '--' in fnames[i]:
                                    cont = 0
                                if cont == 1:
                                    obj.append(fnames[i].split("(")[0])
                            line +=1
                    else:
                        line +=1


        constitutiveLawVariables['flux'] = []
        constitutiveLawVariables['grad'] = []
        constitutiveLawVariables['var_int'] = []
        constitutiveLawVariables['var_aux'] = []
        constitutiveLawVariables['var_extra'] = []
        parser("Flux", constitutiveLawVariables['flux'])
        parser("Grad", constitutiveLawVariables['grad'])
        parser("var_int", constitutiveLawVariables['var_int'])
        parser("var_aux", constitutiveLawVariables['var_aux'])
        parser("Extra Zmat", constitutiveLawVariables['var_extra'])
        #print("constitutiveLawVariables['var_int']   =", constitutiveLawVariables['var_int'])
        #print("constitutiveLawVariables['var_aux']   =", constitutiveLawVariables['var_aux'])
        #print("constitutiveLawVariables['var_extra'] =", constitutiveLawVariables['var_extra'])
        os.system("rm -rf "+tmpFile+"materialtest"+suffix+".py")

        constitutiveLawVariables['var'] = constitutiveLawVariables['grad'] + constitutiveLawVariables['flux'] + constitutiveLawVariables['var_int'] + constitutiveLawVariables['var_aux'] + constitutiveLawVariables['var_extra']

        #Initialize Zmat quantities
        constitutiveLawVariables['cmname']      = materialFileName
        constitutiveLawVariables['nstatv']      = len(constitutiveLawVariables['var_int']) + len(constitutiveLawVariables['var_aux']) +  len(constitutiveLawVariables['var_extra'])
        constitutiveLawVariables['ndi']         = 3
        constitutiveLawVariables['nshr']        = 3
        constitutiveLawVariables['ntens']       = constitutiveLawVariables['ndi'] + constitutiveLawVariables['nshr']
        constitutiveLawVariables['statev']      = np.zeros(constitutiveLawVariables['nstatv'])
        constitutiveLawVariables['ddsddt']      = np.zeros(constitutiveLawVariables['ntens'])
        constitutiveLawVariables['drplde']      = np.zeros(constitutiveLawVariables['ntens'])
        constitutiveLawVariables['stress']      = np.zeros(6)
        constitutiveLawVariables['ddsdde']      = np.zeros((6,6),dtype=np.float)
        constitutiveLawVariables['sse']         = 0.
        constitutiveLawVariables['spd']         = 0.
        constitutiveLawVariables['scd']         = 0.
        constitutiveLawVariables['rpl']         = 0.
        constitutiveLawVariables['drpldt']      = 0.
        constitutiveLawVariables['stran']       = np.zeros(6)
        constitutiveLawVariables['dstran']      = np.zeros(6)
        constitutiveLawVariables['timesim']     = np.array([0.,0.1])
        constitutiveLawVariables['dtime']       = 1.
        constitutiveLawVariables['temperature'] = 0.
        constitutiveLawVariables['dtemp']       = 0.
        constitutiveLawVariables['predef']      = np.zeros(1)
        constitutiveLawVariables['dpred']       = np.zeros(1)
        constitutiveLawVariables['nprops']      = 1
        constitutiveLawVariables['props']       = np.zeros(constitutiveLawVariables['nprops'])
        constitutiveLawVariables['coords']      = np.zeros(3, dtype= float)
        constitutiveLawVariables['drot']        = np.zeros((3,3), dtype= float)
        constitutiveLawVariables['pnewdt']      = 1.
        constitutiveLawVariables['celent']      = 1.
        constitutiveLawVariables['dfgrd0']      = np.zeros((3,3), dtype = float)
        constitutiveLawVariables['dfgrd1']      = np.zeros((3,3), dtype = float)
        constitutiveLawVariables['noel']        = 0
        constitutiveLawVariables['npt']         = 0
        constitutiveLawVariables['kslay']       = 1
        constitutiveLawVariables['kspt']        = 1
        constitutiveLawVariables['kstep']       = np.array([1,1,0,0], dtype=int)
        constitutiveLawVariables['kinc']        = 1

        constitutiveLaw.SetConstitutiveLawVariables(constitutiveLawVariables)

        os.chdir(curFolder)


        return constitutiveLaw


    if behavior == "linear_elastic":

        from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import MecaUniformLinearElasticity as MULE

        data = ZIO.ReadInp2(folder + materialFileName, startingNstar=3)
        elasticity = ZIO.GetFromInp(data,{'3':['behavior'], '2':['elasticity']})[0]

        ranks = {}
        for i in range(3):
            ranks[elasticity[i][0]] = i

        if elasticity[ranks['elasticity']][1] != "isotropic":
            raise ValueError("only isotropic elasticity available for linear-elastic laws")#pragma: no cover

        young = float(elasticity[ranks['young']][1])
        if young =="temperature":
            raise ValueError("only uniform young available for linear-elastic laws")#pragma: no cover

        poisson = float(elasticity[ranks['poisson']][1])

        return MULE.TestMecaConstitutiveLaw(set, young, poisson, density)

    else:
        raise ValueError("behavior law of type "+behavior+" not known")#pragma: no cover



def UpdateFileName(fileName):

    if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
        stem = str(Path(fileName).stem)
        suffix = str(Path(fileName).suffix)
        fileName = stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix

    return fileName



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
