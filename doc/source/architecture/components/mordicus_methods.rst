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
    | Incremental POD                       |   Safran         |   consistent dimensions       | previous iteration      |
    |                                       |                  |                               |                         |
    |                                       |                  | + scalar product matrix       |                         |
    |                                       |                  |   (optional)                  |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **Explore parameter space, reduce parameter complexity**                                                           |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | + solutions vectors with      | Tensor-Train at previous|
    |                                       |  Phiméca (1.1a)  |   consistent dimensions       | iteration               |
    | Low-rank decomposition                |                  |   and a sparse tensor         |                         |
    | (to be clarified)                     |  Mines   (1.1c)  |   format                      |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               | training set            |
    | Greedy reduced basis, e.g. PREIM      |  EDF             |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |  CT              |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **Reduce evaluation cost, reduce operator complexity (operator compression)**                                      |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  | + FE or FV operators (e.g.    | reduced basis           |
    | Galerkin projection onto reduced      |  EDF             |   matrices for viscous and    |                         |
    | space (e.g. POD-Galerkin for NS)      |                  |   convective terms)           |                         |
    |                                       |  Sorbonne        |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |  Safran          | + initial condition           |                         |
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
    |                                       |  Cemosis         | + primal solution vectors     |                         |
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
    |                                       |  Cemosis         |                               |                         |
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
    |                                       |                  |                               |                         |
    |                                       |  CT              |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |  Sorbonne (1.1ef)|                               | reduced basis (built    |
    | NIRB                                  |                  |                               | from fine mesh)         |
    |                                       |  EDF      (1.2h) |                               |                         |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               | - reduced basis         |
    | GEIM                                  |  Cemosis (1.1d)  | linear form to approximate    |                         |
    |                                       |                  |                               | - linear form to        |
    |                                       |                  |                               |   approximate           |
    |                                       |                  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    | **Reconstruction and data assimilation**                                                                           |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |  - reduced basis              | - observed signals      |
    | PBDW                                  |  EDF             |  - scalar product             | - sensor metadata       |
    |                                       |                  |                               | - Riesz representers    |
    |                                       |  Sorbonne        |                               |   of sensors            |
    |                                       |                  |                               |                         |
    |                                       |  Cemosis (1.1d)  |                               |                         |
    +---------------------------------------+------------------+-------------------------------+-------------------------+
    |                                       |                  |                               |                         |
    | Gappy POD                             |  EDF             | + solutions vectors with      |                         |
    |                                       |                  |   consistent dimensions       |                         |
    |                                       |  Mines           |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |  Sorbonne        |                               |                         |
    |                                       |                  |                               |                         |
    |                                       |  Safran          |                               |                         |
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
    |                                       |  CT              |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | **Reduce evaluation cost, reduce operator complexity (operator compression)**                                    |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    | Galerkin projection onto reduced      |  EDF             |   assemble operators    |  recombines precomputed     |
    | space (e.g. POD-Galerkin for NS)      |                  | on the reduced basis    |  small size operators       |
    |                                       |  Cemosis         |  without approximation  |                             |
    |                                       |                  |                         |                             |
    |                                       |  Sorbonne        |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |  Safran          |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | - compute non-linear    |                             |
    | EIM                                   |  EDF             |   term for some         |                             |
    |                                       |                  |   solution              | compute coefficient for     |
    |                                       |  Cemosis         |                         | given parameter             |
    |                                       |                  | - compute affine        |                             |
    |                                       |                  |   decomposition of a    |                             |
    |                                       |                  |   term                  |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | - compute integral of   |  compute reduced quadrature |
    | Empirical quadrature (ECM, ECSW)      |  Safran          |   solution against some |                             |
    |                                       |                  |   test function         |                             |
    |                                       |                  |                         |                             |
    |                                       |  EDF             | - provide Gauss points  |                             |
    |                                       |  Cemosis         |   weights and location  |                             |
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
    |                                       |                  |                         |                             |
    |                                       |  CT              |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         | compute solution on coarse  |
    | NIRB                                  |  Sorbonne (1.1ef)|                         | mesh                        |
    |                                       |                  |                         |                             |
    |                                       |  EDF      (1.2h) |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | - compute linear forms  | - compute linear form at    |
    |                                       |                  |   for some solutions    |   the interpolation points  |
    | GEIM                                  |  Cemosis (1.1d)  |                         |                             |
    |                                       |                  | - perform greedy        | - solve the algebraic       |
    |                                       |                  |   algorithm to compute  |   problem to find the       |
    |                                       |                  |   the basis and the     |   coefficient for a given   |
    |                                       |                  |   matrix of coefficient |   paramater                 |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    | **Reconstruction and data assimilation**                                                                         |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  | compute scalar product  | - get observation           |
    | PBDW                                  |  EDF             |                         |                             |
    |                                       |  Sorbonne        |                         | - solve mixed problem       |
    |                                       |  Cemosis (1.1d)  |                         |                             |
    |                                       |                  |                         |                             |
    |                                       |                  |                         |                             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
    |                                       |                  |                         |                             |
    | Gappy POD                             |  EDF             | - Compute modes         |                             |
    |                                       |  Mines           | - Compute a mask        |  Fit online prediction on   |
    |                                       |  Sorbonne        | (both can be done       | modes values on mask        |
    |                                       |  Safran          | via DEIM)               |  (least square)             |
    +---------------------------------------+------------------+-------------------------+-----------------------------+
