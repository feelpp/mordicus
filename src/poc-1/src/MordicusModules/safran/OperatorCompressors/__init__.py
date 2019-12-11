# -*- coding: utf-8 -*-

"""
All files in this folder must implement two functions:
    - OnlineComputeRegression:
    
    Compute the online stage using the proposed algorithm, this function sets the attribute "coefficients" of compressedSnapshots, the time sequence in compressedSnapshots must have been initialized.
    
    for parametric problems: the parameters must have been initialized in onlineProblemData, 
    for nonparametric problems: the loading must have been initialized in onlineProblemData.
        
    Parameters
    ----------
    operatorCompressionOutputData : Internal Format
        precomputation made by the offline stage
    onlineProblemData : ProblemData
        definition of the testing configuration data in a CollectionProblemData object 
    compressedSnapshots : ModesAndCoefficients
        compressed solution whose attribute "coefficients" is set
                
        
    - OperatorCompressionOffline:
    
    Compress solutions of name "solutionName" from all ProblemDatas in collectionProblemData, and update to corresponding solution.compressedSnapshots in the format ModesAndCoefficients.
        
    Parameters
    ----------
    collectionProblemData : CollectionProblemData
        definition of the training data in a CollectionProblemData object 
    solutionName : str
        name of the solution to be treated
    operatorCompressionInputData : Internal Format
        input needed by the method
                
    Returns
    -------
    operatorCompressionOutputData : Internal Format
        precomputation made by the offline stage
"""

__all__ = ["NonlinearMechanics"]
