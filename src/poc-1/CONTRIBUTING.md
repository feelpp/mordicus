    Please read the following page before contributing code :

        https://www.python.org/dev/peps/pep-0008/

    The only deviations from PEP 8 are the following :

      Function Names: "CamelCase"

        CamelCase starting with uppercase

      Variables Names: "camelCase"

        camelCase starting with lowercase

      Line limit length of 79 characters


    The following rules have been followed:

    a). API are kept simple and evolutive.

    b). Data structures are defined in Containers. ContainerBase contain parent
	classes, and all parameters and function common to all children are
    given in this class. Containers contain Get() and Set() functions for the
	parameters of the class, and we limit the number of advanced functions in
	these classes at maximum. All Set() functions must start by asserting the
	type of the parameter being affected.
	Advanced functions are defined in files from other folders: these files
	do not contain more classes, but act on the classes defined in Containers.

    c). Unitary tests are in Containers classes and functional tests in other
	more advanced classes. The latter also serve as exemples and client code
	for the library.
	
    d). All classes derive derive from a "BaseObject" class that contains a private
	parameter named __storage and initialized to None. This is used in the
	library to contain object for which we do not want to expose the structure in
	the client code. It is accessible through the GetInternalStorage() function.

    e). Solution, ProblemData and CollectionProblemData are the only containers that
	cannot be personalized in the library: other containers inherits from "Base"
	containers, and one can implement another container inheriting from this
	base and respecting the API.

    f). Each folder contains at most one class. 

    g). CheckIntegrities must be local (fewer imports as possible), aiming to test
    only the functions defined in the file, as possible. All functions
    in the file must be tested, if possible (for base classes, common functions 
    over the children that are factorized in the "Base" and "Tools" may
    not be tested in the "Base" and "Tools" files). Please limit the use of functions
    from other file to reach that goal, and use small and simple data, otherwise
    changes will be painful to propagate if many CheckIntegrities must be updated
    as well.

    h). Private parameters of class start with __. They are not part of the
	standard API. They can be accessed using GetInternal functions, but
	their use is not recommanded and requires advanced knowledge of the
	underlying objects.

    i). Coverage must be kept to 100%. 
    
    j). Favor imports at the beginning of files (to be available for CheckIntegrities
    as well without repeat)
    
    k). All customizable containers are in folders in Containers, that contain a "Base" file defining the API to satify, and a "Tools" files that are available functions on these objects. The functions are required for particular use-cases, but are not part of the obect standard API. Moreover, the functions in "Tools" can be execetued for any new introdcued format as long as the standard API defined in "Base" is respected (but are optimzed for one format only).
    
