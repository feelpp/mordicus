import json
from jschon import Catalogue, JSON, JSONSchema
from jschon.exceptions import CatalogueError
import numpy as np
import os
import os.path as osp

class ExportToJSONVisitor(object):
    """
    Abstract visitor
    """
    def __init__(self, folder, solutionReader=None, reconstruct=False):
        """
        Initializes visitor
        """
        self.reconstruct = reconstruct
        self.folder = folder
        self.solutionReader = solutionReader

    def visitCPD(self, cpd):
        """
        Visit Collection Problem Data Structure
        """
        root = {"CollectionProblemData": {}}

        quantityDefinitions = cpd.quantityDefinition.accept(self)
        root["CollectionProblemData"]["quantityDefinitions"] = quantityDefinitions
        variabilityDefinitions = cpd.variabilityDefinition.accept(self)
        root["CollectionProblemData"]["variabilityDefinitions"] = variabilityDefinitions

        # if cpd.reducedTemplateDataset is not None:
        #     subelement = cpd.reducedTemplateDataset.accept(self, cpd)
        #     root["CollectionProblemData"].append(subelement)

        if self.reconstruct:
            # save solution structures
            if cpd.solutionStructures:
                elts = []
                for quantity, structure in cpd.solutionStructures.items():
                    elts.append(structure.accept(self, quantity))
                    root["CollectionProblemData"]["solutionStructures"] = elts
                    
            # save reduced bases
            elts = []
            for quantity, basis in cpd.reducedOrderBases.items():
                filepath = osp.join(self.folder, "reducedOrderBasis" + quantity)
                
                # Try to write it to custom format, otherwise to numpy
                try:
                    self.solutionReader.WriteReducedOrderBasis(filepath, cpd.solutionStructures[quantity], basis, quantity)
                except Exception:
                    if osp.exists(filepath):
                        os.remove(filepath)
                    filepath = filepath + ".npy"
                    np.save(filepath, basis)
                elts.append({"path": filepath, "quantity": quantity })
            root["CollectionProblemData"]["reducedOrderBases"] = elts

            # save problem datas
            elts = []
            for paramValues, problemData in cpd.problemDatas.items():
                params = []
                param_names = [k for k in cpd.variabilityDefinition.keys()]
                for i, val in enumerate(paramValues):
                    params.append({"value":val, "name":param_names[i]})
                    
                pb_data = problemData.accept(self)
                elts.append({"params": params, "ProblemData": pb_data})
            root["CollectionProblemData"]["problemDatas"] = elts

        # loop operatorCompressionData
        elts = []
        for key, reducedOperator in cpd.operatorCompressionData.items():
            # Try exporting through reader, and numpy if this fails
            filepath = osp.join(self.folder, "reducedOperator" + key)
            try:
                self.solutionReader.WriteOperatorCompressionData(filepath, key, cpd)
            except Exception:
                if osp.exists(filepath):
                    os.remove(filepath)
                filepath = filepath + ".npy"
                np.save(filepath, reducedOperator)
            elts.append({"path": filepath, "key": key})
        root["CollectionProblemData"]["operatorCompressionData"] = elts

        return root

    def visitSolutionStructure(self, structure, quantity):
        """
        Visit Solution Structure
        """
        filepath = osp.join(self.folder, "solutionStructure" + quantity)
                
        # It would be cool to have a file extension attribute to solutionStructure
        self.solutionReader.WriteSolutionStructure(filepath, structure, quantity)
        structureElement.text = filepath
        return {"path": filepath, "quantity": quantity, "derivedType": type(structure).__name__}

    def visitDataSet(self, dataset, cpd):
        """
        Visit Dataset
        """
        attrib = {"derivedType"     : type(dataset).__name__,
                  "produced_object" : type(dataset.produced_object).__name__,
                  "solver"          : dataset.solver.id}

        # Handle input_data
        input_data = dataset.input_data
        
        # Copy the content of input_root_folder
        dest = osp.join(self.folder, "reducedDataset")
        shutil.copytree(input_data["input_root_folder"], dest)
        attribData = {}
        attribData["input_root_folder"] = dest
        
        # Copy input_main_file and input_instruction_file if not already in tree
        cwd = os.getcwd()
        os.chdir(input_data["input_root_folder"])
        try:
            for key in ("input_main_file", "input_instruction_file"):
                if key in input_data:
                    if not osp.abspath(osp.realpath(input_data[key])).startswith(input_data["input_root_folder"]):
                        dest = osp.join(self.folder, "reducedDataset", osp.basename(input_data[key]))
                        shutil.copy2(input_data[key], dest)
                        attribData[key] = dest
                    else:
                        attribData[key] = input_data[key]
        finally:
            os.chdir(cwd)
            
        # Copy input_result_type and input_result_path
        for key in ("input_result_type", "input_result_path"):
            attribData[key] = str(input_data[key])      
            
        # mordicus_input_data: loop over keys:
        #     - if key is "modes": reference reducedOrderBases
        #     - if key is in operatorCompressionData: reference reducedOperator<key>
        #     - otherwise, copy and reference original path
        inputMordicus = []
        for key, value in input_data["input_mordicus_data"].items():
            if key in ("modes", ):
                inputModes = []
                for k in value.keys():
                    inputModes.append({"quantity": k, "path": osp.join(self.folder, "reducedOrderBasis"+k)})
                inputMordicus.append(inputModes)
            elif key in cpd.operatorCompressionData:
                inputMordicus.append({"key": key, "path": osp.join(self.folder, "reducedOperator" + key)})
            else:
                cwd = os.getcwd()
                os.chdir(input_data["input_root_folder"])
                try:
                    if not isinstance(value, str):
                        value = value.GetInternalStorage()
                    if not osp.abspath(osp.realpath(value)).startswith(input_data["input_root_folder"]):
                        dest = osp.join(self.folder, "reducedDataset", osp.basename(value))
                        if osp.isdir(value):
                            shutil.copytree(value, dest)
                        else:
                            shutil.copy2(value, dest)
                        path = dest
                    else:
                        path = value
                finally:
                    os.chdir(cwd)
                inputMordicus.append({"key": key, "path": path})

        attribData["inputMordicusDatas"] = inputMordicus
        attrib["inputData"] = attribData

        return attrib

    def visitQuantityDefinitionDict(self, defdict):
        """Visit quantity definition dictionary"""
        elts = []
        for name, (full_name, unit) in defdict.items():
            elts.append({"name":name, "full_name":full_name, "unit":unit})
        return elts

    def visitVariabilityDefinitionDict(self, defdict):
        """Visit variability definition dictionary"""
        elts = []
        for name, valdict in defdict.items():
            attrib = valdict.copy()
            attrib["name"] = name
            for k, v in valdict.items():
                if k == "type":
                    attrib[k] = v.__name__
                if k == "quantity":
                    attrib[k] = v[0]
            elts.append(attrib)
        return elts

    def visitProblemData(self, problemData):
        """Visit problemData"""
        elts = []
        for quantity, solution in problemData.solutions.items():
            elts.append(solution.accept(self))
        return elts

    def visitSolution(self, solution):
        """Visit solution"""
        attrib = {"quantity": solution.solutionName,
                  "nbeOfComponents": solution.nbeOfComponents,
                  "numberOfNodes": solution.numberOfNodes, 
                  "primality": str(solution.primality).lower()}
        elts = []
        for t, arr in solution.compressedSnapshots.items():
            elts.append({"time": str(t), "values": np.array2string(arr, precision=8)})
        attrib["compressedSnapshots"] = elts
        return attrib

    def visitSolver(self, solver):
        """Visit Solver"""
        attrib = {"id": solver.id,
                  "solver_call_procedure_type": solver.solver_call_procedure_type,
                  "call_script": solver.call_script}
        cfgs = []
        for key, value in solver.solver_cfg:
            cfgs.append({"name": key, "value": value})
        attrib["SolverConfiguration"] = cfgs
        return attrib


def exportToJSON(folder, cpd, solutionReader=None, reconstruct=False):
    """
    Export study to a folder with directing JSON file
    """
    os.makedirs(folder, exist_ok=True)
    visitor = ExportToJSONVisitor(folder, solutionReader=solutionReader, reconstruct=reconstruct)
    root = visitor.visitCPD(cpd)
    with open(osp.join(folder, "reducedModel.json"), "w") as out_file:
        json.dump(root, out_file, indent=2)

def checkValidity(json_path):
    """
    Checks validity of JSON file
    """
    try:
        Catalogue.create_default_catalogue('2020-12')
    except CatalogueError:
        pass
    with open(osp.join(osp.dirname(__file__), "Mordicus.json")) as schema_file:
        schema = JSONSchema(json.load(schema_file))
    with open(json_path) as json_file:
        json_doc = JSON(json.load(json_file))
    return schema.evaluate(json_doc)
