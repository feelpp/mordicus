.. _UC_Sorbonne01:

Sorbonne Use Case
-----------------

*Contexte à ajouter*

.. .. tabularcolumns:: |L|L|L|L|

.. table:: Sorbonne use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Sorbonne01 |   Apply the online stage for the approximation of the solution                      |
  |                     |   of a parameter dependant Navier-Stokes equation                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Accelerate the convergence of NS FE scheme for turbulent flow                     |
  |                     |   with an approach based on a coarse mesh (NIRB)                                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   The online component of Mordicus library                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |   Primary task                                                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   Black-box user / User with knowledge of physics                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   black-box user                  | wants a clear output data                       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   user with kowledge of physics   | wants a reduced-order model that behaves as the |
  |                     |                                   | full-order one from his point of view           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       |  Two meshes, one fine mesh and one coarse mesh                                      |
  |                     |                                                                                     |
  |                     |  Data outputs for several parameters of the FOM on fine mesh                        |
  |                     |                                                                                     |
  |                     |  Data outputs for one parameter for coarse mesh                                     |
  |                     |                                                                                     |
  |                     |  Data outputs for several parameters for fine mesh                                  |
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  Approximation data is produced                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  Process is stopped. User gets information about the failure                        |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  User enters the offline component of Mordicus while                                | 
  |                     |  announcing this particular use of the library                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | User : Fills user input data                                             |
  |                     |          |                                                                          |
  |                     |          | 2 meshes                                                                 |
  |                     |          |                                                                          |
  |                     |          | data input on fine mesh                                                  |
  |                     |          |                                                                          |
  |                     |          | data input on corse mesh                                                 |
  |                     |          |                                                                          |
  |                     |          | Options:                                                                 |
  |                     |          |                                                                          |
  |                     |          | Path for input file and output folder                                    |
  |                     |          |                                                                          |
  |                     |          | Number of RB functions                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | User : demands execution of the online phase                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | System : verifies that input data is well provided                       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        | System : apply POD                                                       |
  |                     |          |                                                                          |
  |                     |          | Result : Reduced basis                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5        | System : Does a projection of the coarse data on the fine mesh           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6        | System : Compute the approximation                                       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7        | System : Return the solution at the localisation specified               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 8        | System : notifies user of completion                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3a       | Submitted data incomplete : ask user for missing data                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3b       | Wrong file path : exit                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3c       | Size are incoherent between meshes and input data. Exit                  |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7a       | Invalid path : put the solution in the current folder                    |
  +---------------------+----------+------------------------+-------------------------------------------------+

