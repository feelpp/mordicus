# -*- coding: utf-8 -*-
import numpy as np
import os
from mpi4py import MPI
from pathlib import Path

from Mordicus.Core.IO.InputReaderBase import InputReaderBase
from BasicTools.IO import ZebulonIO as ZIO


knownLoadingTags = ["pressure", "centrifugal", "temperature", "initialCondition", "radiation", "convection_heat_flux"]
knownProblemTypes = ["mechanical", "thermal_transient"]


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


def ConstructLoadingsList(inputFileName):
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
    return reader.ConstructLoadingsList()


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

    def __init__(self, inputFileName):
        """
        Parameters
        ----------
        inputFileName : str, optional
        """
        super(ZsetInputReader, self).__init__()

        assert isinstance(inputFileName, str)

        self.inputFileName = inputFileName
        self.inputFile = None



    def SetInputFile(self):
        """
        Sets the inputFile using the parser in BasicTools.IO.ZebulonIO
        """
        if self.inputFile == None:
            self.inputFile = ZIO.ReadInp2(self.inputFileName)
            self.problemType = None
        else:
            return


    def ReadInputTimeSequence(self):
        """
        Reads the time sequence form the inputFile using the parser in BasicTools.IO.ZebulonIO
        """
        self.SetInputFile()
        return ZIO.GetInputTimeSequence(self.inputFile)


    def ConstructLoadingsList(self):

        self.SetInputFile()
        tables = ZIO.GetTables(self.inputFile)
        zSetLoadings = ZIO.GetLoadings(self.inputFile)

        loadings = []
        for key, value in zSetLoadings.items():
            if key in knownLoadingTags:
                for loadList in zSetLoadings[key]:
                    for load in loadList:
                        loadings.append(self.ConstructOneLoading(key, load, tables))
            else:
                print(
                    "Loading '"
                    + key
                    + "' not among knownBCs: "
                    + str([key for key in knownLoadingTags])
                )


        return loadings


    def ConstructOneLoading(self, key, load, tables):
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

            loading = PressureBC.PressureBC(set)

            sequence = tables[load[3]]
            name = load[2]

            coefficients = collections.OrderedDict()
            fieldsMap = collections.OrderedDict()
            for i, time in enumerate(sequence["time"]):
                coefficients[float(time)] = sequence["value"][i]
                fieldsMap[float(time)] = name

            loading.SetCoefficients(coefficients)
            loading.SetFieldsMap(fieldsMap)

            folder = os.path.dirname(self.inputFileName) + os.sep
            if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
                stem = str(Path(name).stem)
                suffix = str(Path(name).suffix)
                fileName = stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
            else:
                fileName = name

            fields = {name: ZIO.ReadBinaryFile(folder + fileName)}

            loading.SetFields(fields)

            return loading

        if key == "centrifugal":

            from Mordicus.Modules.Safran.Containers.Loadings import Centrifugal

            loading = Centrifugal.Centrifugal(set)

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
            for i, time in enumerate(sequence["time"]):
                rotationVelocity[float(time)] = sequence["value"][i]

            centrifugalDirection = np.array([1.,0.,0.]*(indexRotationAxis==1)+[0.,1.,0.]*(indexRotationAxis==2)+[0.,0.,1.]*(indexRotationAxis==3))

            loading.SetCenter(center)
            loading.SetDirection(centrifugalDirection)
            loading.SetCoefficient(centrifugalCoefficient)
            loading.SetRotationVelocity(rotationVelocity)

            return loading


        if key == "radiation":

            from Mordicus.Modules.Safran.Containers.Loadings import Radiation

            loading = Radiation.Radiation(set)

            stefanBoltzmannConstant = float(load[1])
            coefficient = float(load[2])
            sequence = tables[load[3]]

            coefficients = collections.OrderedDict()
            for i, time in enumerate(sequence["time"]):
                coefficients[float(time)] = coefficient*sequence["value"][i]

            loading.SetStefanBoltzmannConstant(stefanBoltzmannConstant)
            loading.SetCoefficients(coefficients)

            return loading


        if key == "convection_heat_flux":

            from Mordicus.Modules.Safran.Containers.Loadings import ConvectionHeatFlux

            loading = ConvectionHeatFlux.ConvectionHeatFlux(set)

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

            loading = Temperature.Temperature(set)

            for info in load[1].values():
                if isinstance(info, dict):
                    timeTable = info['timeTable']
                    fileTable = info['fileTable']


            fieldsMap = collections.OrderedDict()
            for time, file in zip(timeTable, fileTable):
                fieldsMap[time] = file


            folder = os.path.dirname(self.inputFileName) + os.sep
            fields = {}
            for file in fileTable:
                if file not in fields:
                    if MPI.COMM_WORLD.Get_size() > 1: # pragma: no cover
                        stem = str(Path(file).stem)
                        suffix = str(Path(file).suffix)
                        fileName = stem + "-" + str(MPI.COMM_WORLD.Get_rank()+1).zfill(3) + suffix
                    else:
                        fileName = file
                    fields[file] = ZIO.ReadBinaryFile(folder+fileName)

            loading.SetFieldsMap(fieldsMap)
            loading.SetFields(fields)

            return loading


        if key == "initialCondition":

            from Mordicus.Modules.Safran.Containers.Loadings import InitialCondition

            loading = InitialCondition.InitialCondition(set)

            initDofValues = load[1]

            if initDofValues[0] == 'uniform':
                type = "scalar"
                data = float(initDofValues[1])

            elif initDofValues[0] == 'file':  # pragma: no cover
                type = "vector"
                data = ZIO.ReadBinaryFile(os.path.dirname(self.inputFileName) + os.sep + initDofValues[1])

            loading.SetType(type)
            loading.SetData(data)


            return loading



    def ConstructConstitutiveLawsList(self):

        self.SetInputFile()

        problemType = ZIO.GetProblemType(self.inputFile)

        assert problemType in  knownProblemTypes, "problemType "+problemType+" must refer be among "+str(knownProblemTypes)


        materialFiles = ZIO.GetMaterialFiles(self.inputFile)

        constitutiveLawsList = []

        for set, matFile in materialFiles.items():
            constitutiveLawsList.append(self.ConstructOneConstitutiveLaw(matFile, set, problemType))

        return constitutiveLawsList



    def ConstructOneConstitutiveLaw(self, materialFileName, set, problemType):
        """
        1
        """

        import os, sys


        if problemType == "mechanical":

            from Mordicus.Modules.Safran.External.pyumat import py3umat as pyumat
            from Mordicus.Modules.Safran.Containers.ConstitutiveLaws import ZmatConstitutiveLaw as ZCL

            constitutiveLaw = ZCL.ZmatConstitutiveLaw(set)

            folder = os.path.dirname(self.inputFileName) + os.sep

            density = ZIO.GetDensity(folder + materialFileName)
            constitutiveLaw.SetDensity(density)

            behavior = ZIO.GetBehavior(folder + materialFileName)
            constitutiveLaw.SetBehavior(behavior)

            constitutiveLawVariables = {}

            curFolder = os.getcwd()
            os.chdir(folder)


            suffix = ""
            if MPI.COMM_WORLD.Get_size() > 1:
                suffix += "_"+str(MPI.COMM_WORLD.Get_rank()+1).zfill(3)# pragma: no cover

            code="""
import sys
from Mordicus.Modules.Safran.External.pyumat import py3umat as pyumat
import numpy as np

cmname = '"""+materialFileName+"""'

nstatv = 100
ndi = 3
nshr = 3
ntens = ndi+nshr

stress = np.zeros(6)

statev = np.zeros(nstatv)

ddsdde = np.zeros((6,6),dtype=np.float)

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
        dfgrd1=dfgrd1,noel=noel,npt=npt,kslay=kslay,kspt=kspt,kstep=kstep,kinc=kinc)
    """
            f = open("materialtest"+suffix+".py","w")
            f.write(code)
            f.close()

            import sys
            import subprocess
            out = subprocess.run([sys.executable, "materialtest"+suffix+".py"], stdout=subprocess.PIPE).stdout.decode("utf-8")


            outlines = out.split(u"\n")

            seplines = []
            for i in range(len(outlines)):
                if "============================================" in outlines[i]:
                    seplines.append(i)
                if "done with material file reading" in outlines[i]:
                    lastline = i
            outlines = outlines[seplines[seplines.index(lastline-1)-1]:]

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
            os.system("rm -rf materialtest"+suffix+".py")

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
