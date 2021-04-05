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
        structure : Structure
            Structure instance as defined by mordicus datamodel
        vector : nparray
            numpy array of solution to convert

        Returns
        -------
        localFieldType
            field in the local Type
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden")

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
        raise NotImplementedError("This is a virtual method, intended to be overriden")
    
    def symetricGradient(self, field):
        """
        Parameters
        ----------
        field : localFieldType
        
        Returns
        -------
        field : localFieldType
        """
        raise NotImplementedError("This is a virtual method, intended to be overriden")

    def doublContractedProduct(self, field1, field2):
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
        raise NotImplementedError("This is a virtual method, intended to be overriden")

    def integral(self, field, componentNumber):
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
        raise NotImplementedError("This is a virtual method, intended to be overriden")

        