.. _UC_Cemosis01:

Cemosis Use Case
----------------

*Contexte à ajouter*

.. .. tabularcolumns:: |L|L|L|L|

.. table:: Cemosis use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Cemosis01  |   Reduction of a 3D aerothermal model with data assimilation                        |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Expert user establishes the needed autonomous data structure for running a        |
  |                     |   reduced order simulation of a parametric aerothermal simulation, with non-linear  |
  |                     |   operators dependant of the parameters and the state. Use of the PBDW algorithm    |
  |                     |   for data assimilation from sensors.                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   Offline component of Mordicus library                                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |   Primary task                                                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   User with knowledge of reduced-order modeling techniques                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   User of a reduced order model   | - wants a reduced-order model that behaves as   |
  |                     |   in his field                    |   the full-order one from his point of view;    |
  |                     |                                   |                                                 |
  |                     |                                   | - wants clear and direct access to varying      |
  |                     |                                   |   parameters and physical case description      |
  |                     |                                   |   (for control)                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   Building manager                | wants a clear view of energetic consumption     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |  Preconditions      |  - Full order case of study                                                         |
  |                     |                                                                                     |
  |                     |  - Localisation of sensors                                                          |
  |                     |                                                                                     |
  |                     |  - Data from the sensors                                                            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  Expected autonomous data structure was produced                                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  Only the responsible process is stopped. User gets informed about missing or       |
  | protection          |  erroneous input data, or algorithm configuration at failure                        |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  User enters the offline component of Mordicus                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | User input: parameters domain, affine decomposition, polynomial order,   |
  |                     |          | mesh, configuration (solver, options,...), sensors data                  |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | User : demands execution of the online phase                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | System verifies input data                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        | System applies greedy algorithm + PBDW (need (G/D)EIM)                   |
  |                     |          | and produces a reduced order basis                                       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5        | System packs in data structure: basis vector, compressed matrics         |
  |                     |          | and vectors, fixed coefficients, parameters domain, mesh, discretization.|
  |                     |          | Writes it in data bases.                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6        | System notifies user of the end of the processus                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7        | User checks if everything is ok                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3a       | Data is incoherent, system notifies the user and exit.                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5a       | Invalid path, save at default location                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7a       | User does not agree with errors bounds, request additional basis.        |
  |                     |          | Return to step 4                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Related information | Available documentation at docs.cemosis.fr/ibat/0.1                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+

