.. _sphinx-instructions:

===========================
How to generate these pages
===========================

Pulling the repository from EDF
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From EDF, repository can be pulled by the following bash instructions:

.. code-block:: sh

    ./edf-proxy-cli.py # to pass the proxy

    # Will output something like:
    #     http_proxy=proxypac.edf.fr:<PORT>
    #     https_proxy=proxypac.edf.fr:<PORT>

    # Define environment variables as suggested
    export http_proxy=proxypac.edf.fr:${PORT}
    export https_proxy=proxypac.edf.fr:${PORT}

    # Pull repo
    GIT_SSL_NO_VERIFY=true git clone https://rofifo.mat.mines-paristech.fr/bmarchand/RomFileFormat.git

    # User and password as defined by Basile have to be given

Generating the pages
~~~~~~~~~~~~~~~~~~~~

Simply run ``make html`` from the root directory of the repository.


