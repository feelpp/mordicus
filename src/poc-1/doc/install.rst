.. _install_and_test:

========================
Installation and testing
========================



Installation
============

.. _install:


The easiest way is to create a conda environment.
Using any conda package manager, a compatible python environment can be created with:


.. code-block:: bash

    conda env create -p PATH (or -n NAME) -f path/to/mordicus/conda_env.yml

The content of the conda_env.yml file is reproduced below:

.. code-block:: python

    name: mordicus

    channels:
      - conda-forge

    dependencies:
    # Basic python
      - python=3.8
      - mpi4py
      - setuptools
      - pip=20.2
    # Text formating
      - pylint
      - black
    # Test and doc
      - pytest
      - pytest-cov
      - sphinx
    # Numerical simulations
      - numpy>=1.22.1
      - scikit-learn
      - scipy
      - scikit-sparse
    # BasicTools
      - basictools
    # Option for modules (uncomment to install)
    # Phimeca
    #  - openturns
    # To generate documentation
      - pip:
        - sphinx-rtd-theme
        - sphinxcontrib-bibtex
        - sphinxcontrib-plantumls


Optional Module dependencies
----------------------------

Phimeca
~~~~~~~
    Openturns (uncomment line in conda_env.yml)

Safran
~~~~~~
    To use the Z-mat constitutive law solver, the finite
    element code Z-set must be installed, with update environment variables
    (in particular Z7PATH, PATH, LD_LIBRARY_PATH) - and licenses must be available.
    Then, the Z-mat wrapper must be compiled:

    .. code-block:: bash

        cd path/to/mordicus/src/Mordicus/Modules/Safran/External/pyumat
        make

    To use the mfront constitutive law, the pythnon modules of mfront must
    be installed, see `Mfront python modules <http://tfel.sourceforge.net/mfront-python.html>`_.


Testing
=======

There are two different type of tests, both using pytest and both checking non-regression
by comparaison the produced values with precomputed references.

Unit testing
------------

Checks all functions and producing a coverage report.

Core
~~~~

.. code-block:: bash

    cd path/to/mordicus/tests/Core
    pytest --cov=../../src/Mordicus/Core --cov-report=html:path/to/bluid/html


Safran
~~~~~~

.. code-block:: bash

    cd path/to/mordicus/tests/Modules/Safran
    pytest --cov=../../src/Mordicus/Core --cov-report=html:path/to/bluid/html


Simplified physical use cases
-----------------------------

Illustrate the functionalities of the library in complete use cases.

Core
~~~~

.. code-block:: bash

    cd path/to/mordicus
    pytest src/poc-1/examples/Core


Safran
~~~~~~

Sequential and parallel examples

.. code-block:: bash

    cd path/to/mordicus
    pytest -m "not mpi" src/poc-1/examples/Modules/Safran
    mpirun -n 2 pytest -m "mpi" src/poc-1/examples/Modules/Safran



