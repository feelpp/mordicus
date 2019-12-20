.. _UC_Mines01:

Mines Use Case
--------------

*Contexte à ajouter*

.. .. tabularcolumns:: |L|L|L|L|

.. table:: Mines use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Mines01    |   Construction and equivalent usage of ROM from full field                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   High fidelity Z-set/Zebulon computation                                           |
  |                     |                                                                                     |
  |                     |   Isn't it rather the offline component of Mordicus                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   User without knowledge of reduced-order modelling technique                       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   User of a reduced-order model   | wants a reduced-order model that behaves as the |
  |                     |   in his field                    | full-order one from his point of view           |
  |                     |                                   |                                                 |
  |                     |                                   | wants clear and direct access to varying        |
  |                     |                                   | parameters and physical case description        |
  |                     |                                   | (for control)                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       |  - High-fidelity problem dataset                                                    |
  |                     |  - Post-processing criterion                                                        |
  |                     |  - Vizualisation reduce model on RID and Full Mesh                                  |
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  Reduce computation is equivalent (according given criterion) to high-fidelity      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  The computation results is different to the full-field one. The reduce computation |
  | protection          |  diverge.                                                                           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  User enters problem description                                                    | 
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | User : enters problem description                                        |
  |                     |          |                                                                          |
  |                     |          | Full mesh, behavior, material parameters, boundary conditions,           |
  |                     |          | time discretisation for one cycle                                        |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | User launch the offline stage                                            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | System : verifiy that dataset is valid and launch the full field         |
  |                     |          | computation for one cycle.                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        | System : collect results of the full field computation and build the     |
  |                     |          | reduced-order basis on nodal data (displacement) and integ data          |
  |                     |          | (stress tensor and cumulated plasticity)                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5        | System : build using a DEIM (or a modification of DEIM)                  |
  |                     |          | the Reduce Integration Domain                                            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6        | User : specify the number of cycle to compute using the reduced model    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7        | System : launch the computation for high number of cycle using the       |
  |                     |          | Ryckelynck’s Hyper Reduction (computation made only on the RID)          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 8        | System rebuild the mechanical on the full mesh                           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3a       | User dataset is not correct --- inform user about the error              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3b       | The full field offline compution doesn’t converge                        |
  |                     |          | inform user about computation error                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3c       | The ROM computation doesn’t converge --- inform user abut divergence     |
  +---------------------+----------+------------------------+-------------------------------------------------+

