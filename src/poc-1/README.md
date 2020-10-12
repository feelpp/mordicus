[![pipeline status](https://gitlab.pam-retd.fr/mordicus/mordicus/badges/master/pipeline.svg)](https://gitlab.pam-retd.fr/mordicus/mordicus/commits/master)   [![Coverage report](https://gitlab.pam-retd.fr/mordicus/mordicus/badges/master/coverage.svg?job=poc-1)](http://mordicus.pages.gitlab.pam-retd.fr/mordicus/coverageReportCore/)


        Reduced Order Modelling library of the FUI project "MOR_DICUS".



**Scientific publications:**


    For Safran's module:

    article 1: A Nonintrusive Distributed Reduced Order Modeling Framework for nonlinear structural mechanics -- application to elastoviscoplastic computations [arXiv](https://arxiv.org/abs/1812.07228)

    article 2: An error indicator-based adaptive reduced order model for nonlinear structural mechanics -- application to fatigue computation of high-pressure turbine blades [open access](https://www.mdpi.com/2297-8747/24/2/41)



1) **DEPENDENCIES**

    python minversion  3.6
    Dependencies :
      - pytest pytest-cov mpi4py appdirs scikit-learn
      - BasicTools, and its dependencies : numpy scipy scikit-sparse vtk sympy pyamg h5py pyparsing Cython sphinx setuptools

    during developement, pylint and black where used

    recommandation: create a compatible conda environment by typing:

    conda env create -f environment.yml
    
    to update the environement, go in the folder containing environment.yml (/src/poc-1) and type:

    conda env update


    When using a cluster with optimized mpi already installed, do not install mpi4py from conda, but using « pip install mpi4py » (having loaded the optimized mpi beforehand)



    REMARK for windows:
        mpi4py does not work on its own, requires MPICH https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi?redirectedfrom=MSDN



2) **DOCUMENTATION**

    Documentation is generated using sphinx in the form of a website by executing the following command in the main folder

	python setup.py build_sphinx



3) **TESTING INFRASTRUCTURE**

    Every file from the src folder must have a file of the same name in the tests folder,
    the contains a function called "test" that takes no
    argument and returns the string "ok" if and only if the test was successful. This function
    is meant to test the code in the corresponding file from the src folder

    The testing and coverage are done using pytest:

    Core:
    go to tests/Mordicus/Core and run
    pytest --cov=../../src/Mordicus/Core --cov-report=html:../../coverageReports/coverageReportCore

    Safran's module:
    go to tests/Mordicus/Modules/Safran and run
    pytest --cov=../../../src/Mordicus/Modules/Safran --cov-report=html:../../../coverageReports/coverageReportModuleSafran

    The Core and all modules must keep 100% coverage independantly.



4) **EXAMPLES**

    Examples are available in the folder examples/
    They can be run by excuting the "mordicusScript" files


5) **CONTRIBUTION**

    see [CONTRIBUTING.md](https://gitlab.pam-retd.fr/mordicus/mordicus/blob/safran/src/poc-1/CONTRIBUTING.md)


6) **Used conda environment for dev**

    see environment.yml
