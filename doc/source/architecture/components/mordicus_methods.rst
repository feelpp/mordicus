.. _mordicus_methods:

Mordicus methods
================

As decided in Copil of december 6th, hereafter is a table of the methods that are to be implemented in Mordicus, and for each:

    * the participants expected to be implementing or using the method;

    * the required input data from the HF solver for the *offline* part;

    * the calls to the solver (if any) that the method necessitates for *online* or *offline* part.

.. .. tabularcolumns:: |L|L|L|L|L|L|

.. table:: Methods and their required inputs (from the solver or not)
    :class: longtable

    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **METHOD**                            | **Participants** | **Input data from solver**    | **Other input data**    |
    +=======================================+==================+===============================+=========================+
    | **Generate a reduced basis (data compression)**                                                                    |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | POD                                   |   all            | + solutions vectors with      |                         |
    |                                       |                  |   consistent dimensions       |                         |
    |                                       |                  |                               |                         |
    |                                       |                  | + scalar product matrix       |                         |
    |                                       |                  |   (optional)                  |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | + solutions vectors with      | reduced basis at        |
    | Incremental POD                       |                  |   consistent dimensions       | previous iteration      |
    |                                       |                  |                               |                         |
    |                                       |                  | + scalar product matrix       |                         |
    |                                       |                  |   (optional)                  |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **Explore parameter space, reduce parameter complexity**                                                           |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               |                         |
    |                                       |  Phiméca (1.1a)  |                               |                         |
    | Low-rank decomposition                |                  |         *???*                 |    *???*                |
    | (to be clarified)                     |  Mines   (1.1c)  |                               |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               | training set            |
    | Greedy reduced basis, e.g. PREIM      |  EDF             |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **Reduce evaluation cost, reduce operator complexity (operator compression)**                                      |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | + FE or FV operators (e.g.    | reduced basis           |
    | Galerkin projection onto reduced      |  EDF             |   matrices for viscous and    |                         |
    | space (e.g. POD-Galerkin for NS)      |                  |   convective terms)           |                         |
    |                                       |  Sorbonne        |                               |                         |
    |                                       |                  | + initial condition           |                         |
    |                                       |                  |                               |                         |
    |                                       |  Cemosis         | + BC terms (matrices          |                         |
    |                                       |                  |   or vectors)                 |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | + FE or FV operators (e.g.    |  reduced basis          |
    |                                       |                  |   matrices for viscous and    |                         |
    |                                       |                  |   convective terms)           |                         |
    |                                       |                  |                               |                         | 
    |                                       |                  | + initial condition           |                         |
    |                                       |                  |                               |                         |
    |                                       |                  | + BC terms (matrices          |                         |
    |                                       |                  |   or vectors)                 |                         |
    | EIM                                   |  EDF             |                               |                         |
    |                                       |                  | + primal solution vectors     |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | + FE or FV operators (e.g.    |  reduced basis          |
    |                                       |                  |   matrices for viscous and    |                         |
    |                                       |                  |   convective terms)           |                         |
    |                                       |                  |                               |                         | 
    |                                       |                  | + initial condition           |                         |
    |                                       |                  |                               |                         |
    |                                       |                  | + BC terms (matrices          |                         |
    |                                       |                  |   or vectors)                 |                         |
    | Empirical quadrature (ECM, ECSW)      |  Safran          |                               |                         |
    |                                       |                  | + dual solution vectors       |                         |
    |                                       |  EDF             |                               |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |  Safran          | + FE or FV operators (e.g.    |  reduced basis          |
    |                                       |                  |   matrices for viscous and    |                         |
    |                                       |  EDF             |   convective terms)           |                         |
    |                                       |                  |                               |                         | 
    |                                       |  Mines           | + initial condition           |                         |
    |                                       |                  |                               |                         |
    |                                       |                  | + BC terms (matrices          |                         |
    |                                       |                  |   or vectors)                 |                         |
    | Hyper-reduction (RID)                 |                  |                               |                         |
    |                                       |                  | + mesh                        |                         |
    |                                       |                  |                               |                         |
    |                                       |                  | + dual solution vector        |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | solution vectors              | reduced basis           |
    | Gaussian process regressor            |  Scilab          |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |  Phiméca         |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |  Sorbonne (1.1ef)|                               | reduced basis (built    |
    | NIRB                                  |                  |                               | from fine mesh)         |
    |                                       |  EDF      (1.2h) |                               |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               |                         |
    | GEIM                                  |  Cemosis (1.1d)  |            *???*              |        *???*            |
    |                                       |                  |                               |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **Reconstruction and data assimilation**                                                                           |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               | - observed signals      |
    | PBDW                                  |  EDF             |                               |                         |
    |                                       |                  |                               | - Riesz representers    |
    |                                       |  Sorbonne        |                               |   of sensors            |
    |                                       |                  |                               |                         |
    |                                       |  Cemosis (1.1d)  |                               | - reduced basis         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               |                         |
    | Gappy POD                             |  EDF             |                               |                         |
    |                                       |                  |           *???*               |       *???*             |
    |                                       |  Mines           |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |  Sorbonne        |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+

The required services from the solver are presented in the table below:

.. table:: Methods and their required services from the solver
    :class: longtable

    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | **METHOD**                            | **Participants** |**Offline calls**        | **Online calls to solver**  |
    +=======================================+==================+=========================+=============================+
    | **Generate a reduced basis (data compression)**                                                                  |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | POD                                   |   all            | scalar product of 2     |                             |
    |                                       |                  | solutions (optional)    |                             |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | scalar product of 2     |                             |
    | Greedy POD                            |                  | solutions (optional)    |                             |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | **Explore parameter space, reduce parameter complexity**                                                         |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    | Low-rank decomposition                |  Phiméca (1.1a)  |          *???*          |          *???*              |
    | (to be clarified)                     |                  |                         |                             |
    |                                       |  Mines   (1.1c)  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | compute solution for    | compute a posteriori error  |
    | Greedy reduced basis, e.g. PREIM      |  EDF             | some parameter value    | indicator                   |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | **Reduce evaluation cost, reduce operator complexity (operator compression)**                                    |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    | Galerkin projection onto reduced      |  EDF             |                         |                             |
    | space (e.g. POD-Galerkin for NS)      |                  |                         |                             |
    |                                       |  Cemosis         |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |  Sorbonne        |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | compute non-linear      |                             |
    | EIM                                   |  EDF             | term for some solution  |                             |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | - compute integral of   |                             |
    | Empirical quadrature (ECM, ECSW)      |  Safran          |   solution against some |                             |
    |                                       |                  |   test function         |                             |
    |                                       |                  |                         |                             |
    |                                       |  EDF             | - provide Gauss points  |                             |
    |                                       |                  |   weights and location  |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |  Safran          |                         |                             |
    | Hyper-reduction (RID)                 |                  |                         |                             |
    |                                       |  EDF             |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |  Mines           |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    | Gaussian process regressor            |  Scilab          |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |  Phiméca         |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         | compute solution on coarse  |
    | NIRB                                  |  Sorbonne (1.1ef)|                         | mesh                        |
    |                                       |                  |                         |                             |
    |                                       |  EDF      (1.2h) |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    | GEIM                                  |  Cemosis (1.1d)  |           *???*         |            *???*            |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | **Reconstruction and data assimilation**                                                                         |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | compute scalar product  |                             |
    | PBDW                                  |  EDF             |                         |                             |
    |                                       |  Sorbonne        |                         |                             |
    |                                       |  Cemosis (1.1d)  |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    | Gappy POD                             |  EDF             |                         |                             |
    |                                       |  Mines           |          *???*          |            *???*            |
    |                                       |  Sorbonne        |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
