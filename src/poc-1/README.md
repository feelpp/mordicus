[![pipeline status](https://gitlab.pleiade.edf.fr/mordicus/mordicus/badges/safran/pipeline.svg)](https://gitlab.pleiade.edf.fr/mordicus/mordicus/commits/safran)   [![Coverage report](https://gitlab.pleiade.edf.fr/mordicus/mordicus/badges/safran/coverage.svg?job=testAndCoverageCore)](https://gitlab.pleiade.edf.fr/mordicus/mordicus/coverage/)


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
    
    conda create --name mordicus python=3.8
    
    conda install -c conda-forge pytest pytest-cov mpi4py appdirs scikit-learn scikit-sparse numpy scipy vtk sympy pyamg h5py pyparsing Cython sphinx setuptools pylint black
    
    REMARK for windows:
        mpi4py does not work on its own, requires MPICH https://docs.microsoft.com/en-us/message-passing-interface/microsoft-mpi?redirectedfrom=MSDN


2) **DOCUMENTATION**

    Documentation is generated using sphinx in the form of a website by executing the following command in the doc folder

	make html


3) **TESTING INFRASTRUCTURE**

    Every file from the src folder must have a file of the same name in the tests folder,
    the contains a function called "test" that takes no
    argument and returns the string "ok" if and only if the test was successful. This function
    is meant to test the code in the corresponding file from the src folder

    The testing and coverage are done using pytest:

	go to the src/poc-1/tests/ folder and type
	pytest --cov=../src --cov-report=html:../coverage_report
	a html report is generated in the src/coverage_report folder;
        running pytest from any folder tests all the CheckIntegrity functions from all the python files in the folder and subfolders
      
    The Core and all modules must keep 100% coverage independantly:
    Exemples for testing an individual folder:

    Core:
    go to tests/Mordicus/Core and run
    pytest --cov=../../src/Mordicus/Core --cov-report=html:../../coverageReports/coverageReportCore

    Safran's module:
    go to tests/Mordicus/Modules/Safran and run
    pytest --cov=../../../src/Mordicus/Modules/Safran --cov-report=html:../../../coverageReports/coverageReportModuleSafran
    
    
4) **EXAMPLES**

    Examples are available in the folder examples/
    They can be run by excuting the "mordicusScript" files
    

5) **CONTRIBUTION**

    see [CONTRIBUTING.md](https://gitlab.pam-retd.fr/mordicus/mordicus/blob/safran/src/poc-1/CONTRIBUTING.md)


6) **Used conda environment for dev**


_libgcc_mutex             0.1                        main    conda-forge

alabaster                 0.7.12                     py_0    conda-forge

atomicwrites              1.3.0                      py_0    conda-forge

attrs                     19.3.0                     py_0    conda-forge

babel                     2.7.0                      py_0    conda-forge

blas                      2.14                   openblas    conda-forge

bzip2                     1.0.8                h516909a_1    conda-forge

ca-certificates           2019.11.28           hecc5488_0    conda-forge

certifi                   2019.11.28               py38_0    conda-forge

cffi                      1.13.2           py38h8022711_0    conda-forge

chardet                   3.0.4                 py38_1003    conda-forge

coverage                  4.5.4            py38h516909a_0    conda-forge

cryptography              2.8              py38h72c5cf5_0    conda-forge

curl                      7.65.3               hf8cf82a_0    conda-forge

cython                    0.29.14          py38he1b5a44_0    conda-forge

docutils                  0.15.2                   py38_0    conda-forge

expat                     2.2.5             he1b5a44_1004    conda-forge

fastcache                 1.1.0            py38h516909a_0    conda-forge

freetype                  2.10.0               he983fc9_1    conda-forge

future                    0.18.2                   py38_0    conda-forge

gmp                       6.1.2             hf484d3e_1000    conda-forge

gmpy2                     2.1.0b1          py38h04dde30_0    conda-forge

h5py                      2.10.0          nompi_py38h513d04c_100    conda-forge

hdf4                      4.2.13            hf30be14_1003    conda-forge

hdf5                      1.10.5          nompi_h3c11f04_1104    conda-forge

icu                       64.2                 he1b5a44_1    conda-forge

idna                      2.8                   py38_1000    conda-forge

imagesize                 1.1.0                      py_0    conda-forge

importlib_metadata        1.1.0                    py38_0    conda-forge

jinja2                    2.10.3                     py_0    conda-forge

joblib                    0.14.0                     py_0    conda-forge

jpeg                      9c                h14c3975_1001    conda-forge

jsoncpp                   1.8.4             hc9558a2_1002    conda-forge

krb5                      1.16.3            h05b26f9_1001    conda-forge

ld_impl_linux-64          2.33.1               h53a641e_7    conda-forge

libblas                   3.8.0               14_openblas    conda-forge

libcblas                  3.8.0               14_openblas    conda-forge

libcurl                   7.65.3               hda55be3_0    conda-forge

libedit                   3.1.20170329      hf8c457e_1001    conda-forge

libffi                    3.2.1             he1b5a44_1006    conda-forge

libgcc-ng                 9.2.0                hdf63c60_0    conda-forge

libgfortran-ng            7.3.0                hdf63c60_2    conda-forge

libiconv                  1.15              h516909a_1005    conda-forge

liblapack                 3.8.0               14_openblas    conda-forge

liblapacke                3.8.0               14_openblas    conda-forge

libnetcdf                 4.7.1           nompi_h94020b1_102    conda-forge

libopenblas               0.3.7                h5ec1e0e_4    conda-forge

libpng                    1.6.37               hed695b0_0    conda-forge

libssh2                   1.8.2                h22169c7_2    conda-forge

libstdcxx-ng              9.2.0                hdf63c60_0    conda-forge

libtiff                   4.1.0                hc3755c2_1    conda-forge

libuuid                   2.32.1            h14c3975_1000    conda-forge

libxcb                    1.13              h14c3975_1002    conda-forge

libxml2                   2.9.10               hee79883_0    conda-forge

lz4-c                     1.8.3             he1b5a44_1001    conda-forge

markupsafe                1.1.1            py38h516909a_0    conda-forge

metis                     5.1.0             he1b5a44_1005    conda-forge

more-itertools            7.2.0                      py_0    conda-forge

mpc                       1.1.0             h04dde30_1006    conda-forge

mpfr                      4.0.2                he80fd80_0    conda-forge

mpmath                    1.1.0                      py_0    conda-forge

ncurses                   6.1               hf484d3e_1002    conda-forge

numpy                     1.17.3           py38h95a1406_0    conda-forge

openssl                   1.1.1d               h516909a_0    conda-forge

packaging                 19.2                       py_0    conda-forge

pip                       19.3.1                   py38_0    conda-forge

pluggy                    0.13.1                   py38_0    conda-forge

pthread-stubs             0.4               h14c3975_1001    conda-forge

py                        1.8.0                      py_0    conda-forge

pyamg                     4.0.0           py38h9de70de_1001    conda-forge

pycparser                 2.19                     py38_1    conda-forge

pygments                  2.5.2                      py_0    conda-forge

pyopenssl                 19.1.0                   py38_0    conda-forge

pyparsing                 2.4.5                      py_0    conda-forge

pysocks                   1.7.1                    py38_0    conda-forge

pytest                    4.6.4                    py38_0    conda-forge

pytest-cov                2.8.1                      py_0    conda-forge

python                    3.8.0                h357f687_5    conda-forge

pytz                      2019.3                     py_0    conda-forge

readline                  8.0                  hf8c457e_0    conda-forge

requests                  2.22.0                   py38_1    conda-forge

scikit-learn              0.21.1           py38h22eb022_0  

scikit-sparse             0.4.4           py38h125a7a5_1001    conda-forge

scipy                     1.3.2            py38h921218d_0    conda-forge

setuptools                42.0.2                   py38_0    conda-forge

six                       1.13.0                   py38_0    conda-forge

snowballstemmer           2.0.0                      py_0    conda-forge

sphinx                    2.2.2                      py_0    conda-forge

sphinxcontrib-applehelp   1.0.1                      py_0    conda-forge

sphinxcontrib-devhelp     1.0.1                      py_0    conda-forge

sphinxcontrib-htmlhelp    1.0.2                      py_0    conda-forge

sphinxcontrib-jsmath      1.0.1                      py_0    conda-forge

sphinxcontrib-qthelp      1.0.2                      py_0    conda-forge

sphinxcontrib-serializinghtml 1.1.3                      py_0    conda-forge

sqlite                    3.30.1               hcee41ef_0    conda-forge

suitesparse               5.6.0                h717dc36_0    conda-forge

sympy                     1.4                      py38_0    conda-forge

tbb                       2019.9               hc9558a2_1    conda-forge

tk                        8.6.10               hed695b0_0    conda-forge

urllib3                   1.25.7                   py38_0    conda-forge

vtk                       8.2.0           py38hd1c59f8_205    conda-forge

wcwidth                   0.1.7                      py_1    conda-forge

wheel                     0.33.6                   py38_0    conda-forge

xorg-kbproto              1.0.7             h14c3975_1002    conda-forge

xorg-libice               1.0.10               h516909a_0    conda-forge

xorg-libsm                1.2.3             h84519dc_1000    conda-forge

xorg-libx11               1.6.9                h516909a_0    conda-forge

xorg-libxau               1.0.9                h14c3975_0    conda-forge

xorg-libxdmcp             1.1.3                h516909a_0    conda-forge

xorg-libxt                1.2.0                h516909a_0    conda-forge

xorg-xproto               7.0.31            h14c3975_1007    conda-forge

xz                        5.2.4             h14c3975_1001    conda-forge

zipp                      0.6.0                      py_0    conda-forge

zlib                      1.2.11            h516909a_1006    conda-forge

zstd                      1.4.4                h3b9ef0a_1    conda-forge

