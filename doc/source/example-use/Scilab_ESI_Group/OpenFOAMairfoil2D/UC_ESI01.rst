.. _UC_ESI01:

ESI-SCILAB Use Case
-------------------


This is a basic use case meant to validate modes computation for fluid dynamic.
In that case we are computing pressure field around a NACA0012 airfoil depending on the Angle of Attack (AoA).
This use case is the corner stone to start working on more complex use cases such as prediction using interpolation function on modes coefficients, time changing parameter and model export.

.. i .. _ESI_img1:
.. i .. figure:: Modes.png
.. i
.. i    4 first most energetic modes
.. i    
.. i .. _ESI_img2:
.. i .. figure:: Pred.png
.. i
.. i    Pressure field prediction for AoA = 1.2°


.. .. tabularcolumns:: |L|L|L|L|

.. table:: ESI use case
  :class: longtable

  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE ESI01      |    Pressure field around NACA0012 depending on AoA                                  |
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |    Classic context for such a case would be to reduced the model and then export    |
  |                     |    it for further prediction into a system simulation environment                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |    CAE engineer                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   CAE engineer                    | Design and validate ROM                         |
  |                     |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   Engineer/Technician             | Use ROM for visualization or simulation         |
  |                     |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       |   Scilab installation (with MOR toolbox)                                            |
  |                     |   Already-Computed DoE according to the user requirements                           |
  |                     |   (Geometry, operation conditions, parameters)                                      |
  |                     |                                                                                     |
  |                     |                                                                                     |
  |                     |                                                                                     |
  |                     |                                                                                     |
  |                     |                                                                                     |
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |   A representative ROM, that can predict and train fast                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |   Non-representative ROM, or slow prediction                                        |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |   Request from user to CAE engineer                                                 | 
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        |   Enter mesh information                                                 |
  |                     |          |   Nodes, connectivity                                                    |
  |                     |          |   Be careful: Connectivities information must match available nodes ids  |
  |                     |          |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        |   Enter training simulation information                                  |
  |                     |          |   DoE, physical field values over the mesh                               |
  |                     |          |   Be careful: - DoE dimension must match number of training simulation   |
  |                     |          |   - Field values dimension must match mesh entity dimension              |
  |                     |          |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        |   Train the model specifying the method of interest                      |
  |                     |          |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        |   (OPT) Visualize modes and basis energy for first step validation       |
  |                     |          |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5        |   Use trained model to predict behavior for new parameter and            |
  |                     |          |   validate model.                                                        |
  |                     |          |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6        |   Export model for external use                                          |
  |                     |          |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        |                                                                          |
  +---------------------+----------+------------------------+-------------------------------------------------+
