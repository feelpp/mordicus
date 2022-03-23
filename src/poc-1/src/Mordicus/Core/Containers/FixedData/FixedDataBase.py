# coding: utf-8

class FixedDataBase(object):
    '''
    Objects constant to all simulation to reduce with
    '''
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


    def __str__(self):
        res = "I am a FixedDataBase, try instanciating a particular fixed data instead"
        return res

if __name__ == "__main__":# pragma: no cover

    from Mordicus import RunTestFile
    RunTestFile(__file__)