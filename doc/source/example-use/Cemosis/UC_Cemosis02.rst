.. _UC_Cemosis02:

Cemosis Use Case: High Field Magnet
-----------------------------------

A high field magnet involves several different coupled physics.
First, the electricity that runs through the magnet will produce heat because of the Joule losses.
The temperature will change the thermal and electric conductivity of the copper alloys constituting the magnet.
To control the temperature, the magnet will be cooled by a forced water flow.
The current density will produce a magnetic field.
And the thermal dilation and the Lorentz forces will deform the magnet.
Finally, the deformation of the magnet may alter the cooling and hence the electric current.

Since modeling directly such a complicate problem is very difficult, we chose to make some simplification.
First, we place ourselves in a stationary problem, thus eliminating the difficulty of time-dependent problems.
Then, the cooling of the magnet involves a fluid mechanic problem that is very expensive to solve.
We chose to simplify this problem by introducing heat exchange coefficients derived from standard correlation in thermohydraulics.

We have three problems to solve: a nonlinear thermo-electric problem, a magnetostatic problem and a linear elasticity problem.
We will focus on the thermo-electric problem and we will compute the magnetic field by using the Biot-Savart law.
To reduce the nonlinear problem, we will use EIM to interpolate the thermic and electric conductivities, as well as the Joule losses.
We will then create another reduced basis for the Biot-Savart law by using the precedent reduced basis.
Additionnaly, we want to perform a shape optimization of the magnet, thus needing the discrete version of EIM to approximate the integral on the reference domain.
In this case finally, we may want to use EQM to speed up the computation of the magnetic field by the Biot-Savart law.

.. .. tabularcolumns:: |L|L|L|L|

.. table:: Cemosis high field magnet use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Cemosis02  |   Reduction of a non linear multi-physics 3D electro thermic and magnetostatic      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Expert user establishes the needed autonomous data structure for running a        |
  |                     |   reduced order simulation of a parametric multi-physic simulation, with non-linear |
  |                     |   operators dependant of the parameters and the state. Use of the EIM algorithm,    |
  |                     |   with the possibility to use DEIM and EQM for geometrical parametrization.         |
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
  |                     |   LNCMI Engineer                  | wants a clear view of the state of the magnet   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |  Preconditions      |  - Full order case of study                                                         |
  |                     |                                                                                     |
  |                     |                                                                                     |
  |                     |                                                                                     |
  |                     |                                                                                     |
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
  |                     |          | mesh, configuration (solver, options,...)                                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | User : demands execution of the online phase                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | System verifies input data                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        | System applies greedy algorithm (need (D)EIM)                            |
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
  | Related information | Available documentation at http://docs.cemosis.fr/hifimagnet/stable/                |
  +---------------------+----------+------------------------+-------------------------------------------------+

