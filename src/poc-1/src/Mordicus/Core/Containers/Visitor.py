# coding: utf-8
import lxml
import lxml.etree as etree
from lxml.etree import (Element, ElementTree)

import numpy as np

import os
import os.path as osp

import shutil

class ExportToXMLVisitor(object):
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
        # Initiate Element
        root = Element("CollectionProblemData")
        
        # Create elements for dictionary
        attr_dict = ["quantityDefinition", "variabilityDefinition"]
        for attr in attr_dict:
            subelement = getattr(cpd, attr).accept(self)
            root.append(subelement)
        
        if cpd.reducedTemplateDataset is not None:
            subelement = cpd.reducedTemplateDataset.accept(self, cpd)
            root.append(subelement)
        
        if self.reconstruct:
            # save solution structures
            if cpd.solutionStructures:
                root_structures = Element("solutionStructures")
                root.append(root_structures)
                for quantity, structure in cpd.solutionStructures.items():
                    structureElement = structure.accept(self, quantity)
                    root_structures.append(structureElement)

            # save reduced bases
            root_bases = Element("reducedOrderBases")
            root.append(root_bases)
            for quantity, basis in cpd.reducedOrderBases.items():
                basisElement = Element("reducedOrderBasis", attrib={"quantity": quantity})
                filepath = osp.join(self.folder, "reducedOrderBasis" + quantity)
                
                # Try to write it to custom format, otherwise to numpy
                try:
                    self.solutionReader.WriteReducedOrderBasis(filepath, cpd.solutionStructures[quantity], basis, quantity)
                except Exception:
                    if osp.exists(filepath):
                        os.remove(filepath)
                    filepath = filepath + ".npy"
                    np.save(filepath, basis)
                    
                basisElement.text = filepath
                root_bases.append(basisElement)
            
            # save problem datas
            root_pbds = Element("problemDatas")
            root.append(root_pbds)
            for paramValues, problemData in cpd.problemDatas.items():
                root_pbd = Element("problemDataInstance")
                root_pbds.append(root_pbd)
                param_names = [k for k in cpd.variabilityDefinition.keys()]
                for i, val in enumerate(paramValues):
                    param_elem = Element("param", attrib={"name": param_names[i]})
                    param_elem.text = str(val)
                    root_pbd.append(param_elem)
                pbdElement = problemData.accept(self)
                root_pbd.append(pbdElement)
                
                
        # loop operatorCompressionData
        root_reduced_operators = Element("operatorCompressionData")
        root.append(root_reduced_operators)
        for key, reducedOperator in cpd.operatorCompressionData.items():
            # Try exporting through reader, and numpy if this fails
            reducedOperatorElement = Element("reducedOperator", attrib={"key": key})
            filepath = osp.join(self.folder, "reducedOperator" + key)
            try:
                self.solutionReader.WriteOperatorCompressionData(filepath, key, cpd)
            except Exception:
                if osp.exists(filepath):
                    os.remove(filepath)
                filepath = filepath + ".npy"
                np.save(filepath, reducedOperator)
            reducedOperatorElement.text = filepath
            root_reduced_operators.append(reducedOperatorElement)
        
        return root
       
    def visitSolutionStructure(self, structure, quantity):
        """
        Visit Solution Structure
        """
        structureElement = Element("solutionStructure", attrib={"quantity": quantity, "derivedType": type(structure).__name__})
        filepath = osp.join(self.folder, "solutionStructure" + quantity)
                
        # It would be cool to have a file extension attribute to solutionStructure
        self.solutionReader.WriteSolutionStructure(filepath, structure, quantity)
        structureElement.text = filepath
            
        return structureElement
    
    def visitDataSet(self, dataset, cpd):
        """
        Visit Dataset
        """
        # Initialize datasetructure element
        # Solver is only represented by a reference hosted by an attribute
        attrib = {"derivedType"     : type(dataset).__name__,
                  "produced_object" : type(dataset.produced_object).__name__,
                  "solver"          : dataset.solver.id}
        dsElement = Element("reducedDataset", attrib=attrib)
        
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
        inputMordicusElement = Element("inputMordicusDatas")
        for key, value in input_data["input_mordicus_data"].items():
            if key in ("modes", ):
                inputModes = Element("inputMordicusModes")
                for k in value.keys():
                    inputMode = Element("inputMordicusMode", attrib={"quantity": k})
                    inputMode.text = osp.join(self.folder, "reducedOrderBasis" + k)
                    inputModes.append(inputMode)
                inputMordicusElement.append(inputModes)
            elif key in cpd.operatorCompressionData:
                inputMordicusDataElement = Element("inputMordicusData", attrib={"key": key})
                inputMordicusDataElement.text = osp.join(self.folder, "reducedOperator" + key)
                inputMordicusElement.append(inputMordicusDataElement)
            else:
                inputMordicusDataElement = Element("inputMordicusData", attrib={"key": key})
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
                        inputMordicusDataElement.text = dest
                    else:
                        inputMordicusDataElement.text = value
                finally:
                    os.chdir(cwd)
                inputMordicusElement.append(inputMordicusDataElement)
                
        inputDataElement = Element("inputData", attrib=attribData)
        inputDataElement.append(inputMordicusElement)

        dsElement.append(inputDataElement)
        return dsElement
    
    def visitQuantityDefinitionDict(self, defdict):
        """Visit quantity definition dictionary"""
        qdefsElement = Element("quantityDefinitions")
        for name, (full_name, unit) in defdict.items():
            qdefElement = Element("quantityDefinition", attrib={"name": name, "full_name": full_name, "unit": unit})
            qdefsElement.append(qdefElement)
        return qdefsElement

    def visitVariabilityDefinitionDict(self, defdict):
        """Visit variability definition dictionary"""
        varsElement = Element("variabilityDefinitions")
        for name, valdict in defdict.items():
            attrib = valdict.copy()
            attrib["name"] = name
            for k, v in valdict.items():
                if k == "type":
                    attrib[k] = v.__name__
                if k == "quantity":
                    attrib[k] = v[0]
            varElement = Element("variabilityDefinition", attrib=attrib)
            varsElement.append(varElement)
        return varsElement

    def visitProblemData(self, problemData):
        """Visit problemData"""
        pbElement = Element("ProblemData")
        for quantity, solution in problemData.solutions.items():
            solutionElement = solution.accept(self)
            pbElement.append(solutionElement)
        return pbElement
    
    def visitSolution(self, solution):
        """Visit solution"""
        attrib = {"quantity": solution.solutionName,
                  "nbeOfComponents": str(solution.nbeOfComponents),
                  "numberOfNodes": str(solution.numberOfNodes), 
                  "primality": str(solution.primality).lower()}
        solutionElement = Element("Solution", attrib=attrib)
        for t, arr in solution.compressedSnapshots.items():
            snapElement = Element("compressedSnapshot", attrib={"time": str(t)})
            snapElement.text = np.array2string(arr, precision=8)
            solutionElement.append(snapElement)
        return solutionElement
    
    def visitSolver(self, solver):
        """Visit Solver"""
        attrib = {"id": solver.id,
                  "solver_call_procedure_type": solver.solver_call_procedure_type,
                  "call_script": solver.call_script}
        solverElement = Element("ExternalSolvingProcedure", attrib=attrib)
        solverConfiguration = Element("SolverConfiguration")
        for key, value in solver.solver_cfg:
            solverCfgEntry = Element("SolverCfgEntry", attrib={"name": key})
            solverCfgEntry.text = value
            solverConfiguration.append(solverCfgEntry)
        solverElement.append(solverConfiguration)
        return solverElement

def exportToXML(folder, cpd, solutionReader=None, reconstruct=False):
    """
    Export study to a folder with directing XML file
    """
    os.makedirs(folder, exist_ok=True)
    visitor = ExportToXMLVisitor(folder, solutionReader=solutionReader, reconstruct=reconstruct)
    root_element = visitor.visitCPD(cpd)
    tree = ElementTree(root_element)
    tree.write(osp.join(folder, "reducedModel.xml"), 
               encoding='UTF-8',
               pretty_print=True)
    
def checkValidity(xml_path):
    """
    Checks validity of XML file
    """
    xmlschema_doc = etree.parse(osp.join(osp.dirname(__file__), "Mordicus.xsd"))
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)

    try:
        xmlschema.assertValid(xml_doc)
    except etree.DocumentInvalid as xml_errors:
        print ("List of errors:\r\n", xml_errors.error_log)
    return xmlschema.validate(xml_doc)