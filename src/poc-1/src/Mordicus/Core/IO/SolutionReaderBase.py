# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#



class SolutionReaderBase(object):
    """
    Class containing the SolutionReaderBase associated to a HF solution file
    """

    def __init__(self):
        pass


    def ReadSnapshotComponent(self, fieldName, time, primality):
        """
        Reads a snapshots from the solutions of name "fieldName", at time "time" and of primality "primality", from the HF computation

        Parameters
        ----------
        fieldName : str
            name of the solution from which the snapshot is read
        time : float
            time at which the snapshot is read
        primality : bool
            primality of the solution from which the snapshot is read

        Returns
        -------
        np.ndarray
            of size (numberOfDofs,)
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def ReadSnapshotComponentTimeSequence(self, fieldName, timeSequence, primality):
        """
        Reads a snapshots from the solutions of name "fieldName", at time sequence "timeSequence" and of primality "primality", from the HF computation

        Parameters
        ----------
        fieldName : str
            name of the solution from which the snapshot is read
        timeSequence : np.ndarray
            of size (numberOfSnapshots,)
        primality : bool
            primality of the solution from which the snapshot is read

        Returns
        -------
        np.ndarray
            of size (numberOfSnapshots,numberOfDofs)
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def ReadTimeSequenceFromSolutionFile(self):
        """
        Reads the time sequence from the solution file of the HF computation (may be different from the ones defined in the input data file if the solver chose to solve at additional time steps)

        Returns
        -------
        np.ndarray
            of size (numberOfSnapshots,)
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def WriteReducedOrderBasis(self, fileName, solutionStructure, reducedOrderBasis, fieldName):
        """
        Converts Mordicus reduced order basis into the format for writing fields

        Parameters
        ----------
        fileName : str
            file to write reduced basis to
        fieldStructure : SolutionStructureBase
            field structure giving the context to interpret the vector in terms of field values on the mesh
        reducedOrderBasis : nparray(numberOfModes, numberOfDofs)
            numpy array of the modes
        fieldName : str
            name of field associated with the basis (e.g. "U", "sigma")
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def WriteSparseFieldOfEmpiricalWeights(self, fileName, fieldStructure, np_coor_gauss, empirical_weights):
        """
        Writes found empirical_weights to a Gauss field

        Parameters
        ----------
        fileName : str
            file to write field of empirical weights to
        fieldStructure : MEDAsterSolutionStructure
            field structure giving the context to interpret the vector in terms of field values on the mesh
        np_coor_gauss
            numpy array of empirical Gauss points coordinates
        empirical_weights
            numpy array of empirical weights
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def WriteSolution(self, fileName, fieldStructure, solution, fieldName, nameInFile=None, append=False):
        """
        Convert a Mordicus snapshot into a field, relying on SolutionStructure to build relations
        between the vector of values and the mesh.

        Arguments
        ---------
        fileName : str
            MED file to write solution to
        fieldStructure : MEDAsterSolutionStructure
            field structure giving the context to interpret the vector in terms of field values on the mesh
        solution : Solution
            solution to write
        fieldName : str
            identifier of the physical quantity for the field
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def WriteNumbering(self, fileName, fieldStructure, fieldName, nameInFile=None):
        """
        Write an identity application on the input, gets the permutation application on the output.
        This method is used to convert operators from a FEM code to the numbering system associated
            with the format of the results (for instance be able to get a consistent numbering between
            a mass matrix computed with Code_Aster and the results written to MED format)

        Arguments
        ---------
        fileName : str
            MED file to write permutation to
        fieldStructure : SolutionStructureBase
            field structure for which the numbering system has to be converted
        fieldName : str
            identifier of the physical quantity for the field
        nameInFile : str
            to customize field name in output MED file *fileName*
        """
        raise NotImplementedError("Not implemented in ReaderBase")  # pragma: no cover


    def __str__(self):
        res = "I am a SolutionReaderBase, try instanciating a particular reader instead"
        return res



if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)


