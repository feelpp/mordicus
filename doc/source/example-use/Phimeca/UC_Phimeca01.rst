.. _UC_Phimeca01:

Phimeca Use Case
----------------

The broader context of this use-case is the analysis of temporal stochastic processes.
We consider as data N realizations of the process X(w,t) where the time index t
is discretized on a an interval of R, w is a realization of a multivariate random vector,
and X is also possibly multivariate.
Here the process is univariate and each realization consists of a
trajectory (t, Z_t) when t varies in an interval. Each trajectory depends
on one realization of the multivariate joint distribution of some physical parameters.

.. .. tabularcolumns:: |L|L|L|L|

.. table:: Phimeca use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Phimeca01  |   Create a metamodel of a non-linear free-fall solid in a viscous fluid.            |
  |                     |   This is an analytical toy example.                                                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   The context is uncertainty propagation in a field model. Typically we want to     |
  |                     |   build a reduced model (online), then assess its validity against the real model   |
  |                     |   (offline). Finally we want to propagate uncertainties through the reduced model.  |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   Online and offline components of Mordicus                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |   Primary task                                                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   An R&D engineer with knowledge of reduced-order modelling techniques              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   User of a reduced-order model   | Wants fast evaluation of the model to explore   |
  |                     |   in his field                    | the model response to given inputs              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   R&D engineer with knowledge of  | Wants to perform a sensitivity analysis,        |
  |                     |   uncertainty propagation         | threshold exceedance simulation.                | 
  |                     |   methodology                     |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       |   - A computer code with a custom language-specific wrapper                         |
  |                     |                                                                                     |
  |                     |   - Or an already-computed design of experiment                                     |
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  A representative reduced-order model                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  A visually non-representative reduced-order model                                  |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  Begin of the uncertainty propagation study                                         | 
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | User provides X/Y data from the model evaluations and the mesh           |
  |                     |          |                                                                          |
  |                     |          | The input is 4-d, the output is 1-d on a 1-d mesh (regular time grid)    |
  |                     |          |                                                                          |
  |                     |          | The output timeseries are evaluated on the same time grid                |
  |                     |          |                                                                          |
  |                     |          | There should not be nans or missing values                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | User: demands the model to be built (inline)                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | System: checks input data (X/Y size, outputs vs mesh size)               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        | System: apply KarunhenLoeve SVD decomposition, projection of output      |
  |                     |          | series, perform functional chaos in the decomposition space.             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5        | User: demands evaluation on validation input sample (offline)            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6        | System: checks input sample                                              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7        | System: evaluates the model                                              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3a       | Size of inputs differs from the outputs size (the number of input points |
  |                     |          | vs the number of output trajectories                                     |
  |                     |          |                                                                          |
  |                     |          | Inform user and clean exit                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3b       | The output discretization size differs from the provided mesh size       |
  |                     |          |                                                                          |
  |                     |          | Inform user and clean exit                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6a       | The input sample dimension differs from the reduced-order                |
  |                     |          | input dimension                                                          |
  |                     |          |                                                                          |
  |                     |          | Inform user and clean exit                                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
