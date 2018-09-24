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

Installing sphinxcontrib-plantuml python package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following command and it will install onto ``${HOME}/.local/lib/python2.7/site-packages``:

.. code-block:: sh

    edf-proxy-cli.py
    pip install --user --proxy proxypac.edf.fr:3128 sphinxcontrib-plantuml
    # Add to PYTHONPATH
    export PYTHONPATH=${PYTHONPATH}:${HOME}/.local/lib/python2.7/site-packages
    # Check
    echo ${PYTHONPATH} | sed 's/:/\n/g' | grep '.local'

I include the jar file in its last version (0.11), it can be downlodad `on the planuml download page <https://downloads.sourceforge.net/project/plantuml/plantuml.jar?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fplantuml%2Ffiles%2Fplantuml.jar%2Fdownload&ts=1530089699>`_.

Installing Modelio on Debian or Ubuntu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The download page of Modelio can be found `here <https://www.modelio.org/downloads/download-modelio.html>`_.

Download the ``.deb`` file (64-bit for EDF). Then run:

.. code-block:: sh

    chmod 744 modelio-open-source3.7_3.7.1_amd64.deb

    # Install prerequisite
    sudo apt-get install libwebkitgtk-1.0-0

    sudo dpkg -i modelio-open-source3.7_3.7.1_amd64.deb

Modelio is ready to start:

.. code-block:: sh

    modelio-open-source3.7





