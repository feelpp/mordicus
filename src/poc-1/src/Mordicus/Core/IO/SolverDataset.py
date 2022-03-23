# coding: utf-8

import os
import os.path as osp
import shutil
import numpy as np

from Mordicus.Core.Containers.FixedData.FixedDataBase import FixedDataBase
from Mordicus.Core.Containers.ResolutionData.ResolutionDataBase import ResolutionDataBase
from Mordicus.Core.Containers.ProblemData import ProblemData
from Mordicus.Core.Containers.Solution import Solution


class SolverDataset(object):
    """
    Gathers all data to be provided to a *SolvingProcedure*

    Attributes
    ----------
    producedObject : cls
        class of produced python object (after callback is called)
    solver : SolvingProcedure
        solver object associated with the dataset
    inputData : dict
        dictionary of all parameters to be passed to the calling procedure
    """

    def __init__(self, producedObject, solver, inputData):
        """
        Constructor
        """
        self.producedObject = producedObject
        self.solver = solver
        self.inputData = inputData


    def Run(self, **kwargs):
        """
        Executes the dataset with its solver
        """
        if "inputMordicusData" in self.inputData:
            self.solver.importMordicusData(self.inputData)
        scriptAfterSubstitutions = self.solver.callScript.format(**self.inputData, **self.solver.solverCfg)
        if hasattr(self.solver, "PythonPreprocessing"):
            self.solver.PythonPreprocessing(self)
        self.solver.Execute(scriptAfterSubstitutions)
        return self.ExtractResult(**kwargs)


    def ExtractResult(self, extract=None, solutionStructures=None, primalities=None, solutionReaderType=None):
        """
        Calls constructor of object to import the file into a data structure

        Arguments
        ---------
        extract : tuple(str)
            identifier of the solutions to extract (e.g. "U", "sigma"...)
        solutionStructures: dict
            dict with solution name as key and solutionStructure as argument
        primalities: dict
            dict with solution name as key and solutionStructure as argument
        solutionReaderType : type
            specific solution reader to use
        """
        resultFilePath = osp.join(self.inputData["inputRootFolder"], self.inputData["inputResultPath"])
        if self.producedObject == FixedDataBase:
            obj = self.producedObject()
            obj.SetInternalStorage(resultFilePath)
        if self.producedObject == ResolutionDataBase:
            obj = self.producedObject()
            if self.inputData["inputResultType"] == "matrix":
                obj.SetInternalStorage(np.load(resultFilePath))
        if self.producedObject == ProblemData:

            if extract is None or solutionStructures is None or primalities is None:# pragma: no cover
                raise ValueError("To extract a ProblemData, all optional arguments to ExtractResult shall be present")
            # to be changed with the new syntax for defining parameters
            problemData = ProblemData("dummy")

            # create reader and get time sequence
            solutionReader = solutionReaderType(resultFilePath, 0.0)
            outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile(extract[0])

            # loop over field to extract
            for fieldName in extract:

                # primal field
                solutionStructure = solutionStructures[fieldName]
                nbeOfComponents = solutionStructure.GetNumberOfComponents()
                numberOfNodes = solutionStructure.GetNumberOfNodes()
                primality = primalities[fieldName]

                solution = Solution(fieldName, nbeOfComponents, numberOfNodes, primality=primality)

                # Read the solutions from file
                for time in outputTimeSequence:
                    snap = solutionReader.ReadSnapshotComponent(fieldName, time, primality, solutionStructure)
                    solution.AddSnapshot(snap, time)

                problemData.AddSolution(solution)

            return problemData

        return obj


    def Instantiate(self, **kwargs):
        """
        Instantiate a template dataset. Replace parameters in file by their values
        """
        if "reduced" in kwargs and kwargs.pop("reduced"):
            basestr = "runReduced"
        else:
            basestr = "runFull"
        from string import Template
        with open(osp.join(self.inputData["inputRootFolder"], self.inputData["inputInstructionFile"]), "r") as f:
            mystr = f.read()
            mytemplate = Template(mystr)
            kws = {k: str(v) for k,v in kwargs.items()}
            myinstance = mytemplate.safe_substitute(**kws)
        dirbname = basestr
        for k, v in kwargs.items():
            if isinstance(v, float):
                dirbname = dirbname + "_".join(["", str(k), "{:.3e}".format(v)])
            else:
                dirbname = dirbname + "_".join(["", str(k), str(v)])

        # The following does not take into account parameters that are not floats
        # dirbname = basestr + "_".join(["{0}_{1:.3e}".format(k, v) for k,v in kws.items()])

        dirname = osp.join(osp.dirname(self.inputData["inputRootFolder"]), dirbname)
        if osp.exists(dirname):
            shutil.rmtree(dirname)# pragma:no cover
        # Create file in directory name
        os.makedirs(dirname, exist_ok=False)
        targetFile = osp.join(dirname, osp.basename(self.inputData["inputInstructionFile"]))
        with open(targetFile, "w") as f:
            f.write(myinstance)
        #os.chmod(targetFile, 0o755)
        # Using shutil.copy2 to preserve permissions
        targetFile = osp.join(dirname, osp.basename(self.inputData["inputMainFile"]))
        shutil.copy2(osp.join(self.inputData["inputRootFolder"], osp.basename(self.inputData["inputMainFile"])),
                     targetFile)
        #os.chmod(targetFile, 0o755)
        inputData = {"inputRootFolder"       : dirname,
                      "inputMainFile"        : osp.basename(self.inputData["inputMainFile"]),
                      "inputInstructionFile" : osp.basename(self.inputData["inputInstructionFile"]),
                      "inputMordicusData"    : self.inputData["inputMordicusData"],
                      "inputResultPath"      : osp.basename(self.inputData["inputResultPath"]),
                      "inputResultType"      : self.inputData["inputResultType"]}

        return SolverDataset(self.producedObject,
                             self.solver,
                             inputData)

    def __str__(self):
        res = "SolverDataset\n"
        res += "producedObject: " + str(self.producedObject) + "\n"
        res += "solver        : " + str(self.solver) + "\n"
        res += "inputData     : " + str(self.inputData)
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
