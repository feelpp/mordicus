# coding: utf-8

class FieldHandlerBase(object):
    """
    Class containing a FieldHandlerBase, with an internal storage hidden to all its children classes

    Attributes
    ----------
    __storage : typeToDefine
    """

    def __init__(self):
        self.__storage = None


    def SetInternalStorage(self, __storage):
        """
        Sets the internal storage

        Parameters
        ----------
        __storage : typeToDefine
        """
        if self.__storage is not None:
            print(
                "Internal storage already set. Replacing it anyway."
            )  # pragma: no cover
        self.__storage = __storage

    def GetInternalStorage(self):
        """
        Returns
        -------
        typeToDefine
            internal storage
        """
        if self.__storage is None:
            raise AttributeError("Please set internal storage")  # pragma: no cover
        return self.__storage

    def ConvertToLocalField(self, structure, vector):
        """
        Parameters
        ----------
        structure : SolutionStructure
            Structure instance as defined by mordicus datamodel
        vector : nparray
            numpy array of solution to convert

        Returns
        -------
        localFieldType
            field in the local Type
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover

    def ConvertFromLocalField(self, field):
        """
        Parameters
        ----------
        field : localFieldType
            field in the local Type

        Returns
        -------
        np.array:
            numpy array of field values
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover

    def SymetricGradient(self, field, solutionStructureGauss, solutionStructureNode):
        """
        Parameters
        ----------
        field : localFieldType
            local field to derive
        solutionStructureGauss : SolutionStructure
            solution structure of the result
        solutionStructureNode : SolutionStructure
            solutionStructure of the field to derive

        Returns
        -------
        field : localFieldType
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover

    def DoublContractedProduct(self, field1, field2):
        """
        Parameters
        ----------
        field1 : localFieldType
            first symmetric 3x3 tensor s
        field2 : localFieldType
            second symmetric 3x3 tensor e

        Returns
        -------
        s : e, i.e. s(1)*e(1) + s(2)*e(2) + s(3)*e(3) + 2*s(4)*e(4) + 2*s(5)*e(5) + 2*s(6)*s(6)
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover

    def Integral(self, field, componentNumber):
        """
        Parameters
        ----------
        field : localFieldType
            field to integrate over its whole domain Omega
        componentNumber : int
            number of the component number to integrate

        Returns
        -------
        double : integral over Omega of field(componentNumber)
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover

    def GaussPointsCoordinates(self, solutionStructureGauss):
        """
        Get the Gauss point coordinate a family of solutions relies on

        Arguments
        ---------
        solutionStructureGauss
            a solution structure with discretization on Gauss points (any number of components)

        Returns:
        -------
        ndarray
            numpy array of Gauss points coordinates for the given solutionStructureGauss
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover

    def GetVolume(self, solutionStructureGauss):
        """
        Compute volume getting Gauss points from a sample field

        Arguments
        ---------
        solutionStructureGauss
            a solution structure with discretization on Gauss points (any number of components)

        Returns
        -------
        double
            volume of the domain the family of solutions is defined on
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden") # pragma: no cover


    def __str__(self):
        res = "I am a FieldHandlerBase, try instanciating a particular field handler instead"
        return res


if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)
