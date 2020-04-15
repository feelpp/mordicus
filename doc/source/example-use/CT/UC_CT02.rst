.. _UC_CT02:

CT Use Case : Multiphysics coupling between a combustion chamber and cooling circuit channels 
------------------------------------------------------

We propose a hybrid high-order/low-order method to resolve the multi-physics coupling between a combustion chamber and cooling circuit channels. Since the computational cost of the whole multi-physics problem is often prohibitive for industrial applications, solution of this problem is supposed to be not known, or at least not very well approximated by the high-fidelity method. In this work, the main idea is to use, in a online phase, a high-fidelity scheme to discretize the governing equation of the flow in the combustion chamber and in the solid domain. On the other hand, the cooling circuit channels are split into different subdomain with recurrent topological features and are treated with a non-intrusive ROM. The ROM could be based on an iterative method by domain decomposition [1] or by using Galerkin method on reduced spaces [2]. In the latter, a suitable coupling condition across subdomain interfaces is used to guarantee continuity of the solution. Therefore, the use of an efficient domain coupling and training strategy may assume high relevance in this context.

The main interest is the construction of a non-intrusive ROM of cooling circuit channels with parametric boundary conditions: mass flow and temperature at the inlet, outlet pressure, temperature field at the walls of the channel. In the offline phase, different snapshots for a sufficient number of samples are collected in order to represent the solution manifold accurately. 

The model is radially coupled (below) with the solid domain and tangentially with other ROMs. We consider a computational domain Omega of the cooling circuit channels parametrized through mu = (mu_1, mu_2, mu_r) (which represent different boundary conditions) and decomposed in R subdomains Omega_r, each one parametrized through the corresponding mu_r. Here R is the number of channels.
The offline stage consists of the computation of independent reduced basis spaces by using an accurate fine mesh with the high fidelity solver. We solve problems for several values of the (sampling) parameter mu_r and we define the corresponding reduces spaces. The boundary condition may correspond in portions of the wall temperature retrieved from a high-fidelity chamber computation with either adiabatic boundary condition or prescribed temperature or heat flux.
During the online phase, we use the results of the previous stage and we could consider some proper computations and additional gluing conditions through the internal interfaces, in order to find a continuous global solution in the domain Omega [2].
In particular, at every solver iteration and for every given new parameter mu = (mu_1, mu_2, mu_r), a high-fidelity solution of the problem could be computed in a fast way by using a (very) coarse mesh on the whole domain of the cooling circuit channels. We restrict these functions to each subdomain Omega_r by interpolating these coarse solutions on the fine mesh. These functions are obviously continuous along the internal interfaces and they bring important physical information.
In each subdomain we define the reduced space as constituted of the set of basis functions (computed offline) on the fine accurate mesh and, eventually, adding the approximation of the whole problem on the coarse grid (computed online).
The global reduced basis solution is defined by a suitable local linear combination of the precomputed functions on each subdomain. The coefficients of the linear combination are determined by the iterative procedure described in [1] and detailed below or by using the (a posteriori) Galerkin method on the reduced space [2][3]. Since the reduced spaces are made of discontinuous functions, their jumps across the interfaces of the channels could be minimized through the use of Lagrange multipliers. Least-squares estimation using Lagrange multipliers may be used to preserve the total mass flow rate of the cooling circuit channels.

As for the iterative procedure described in [1] and [4], boundary condition (temperature or heat flux) at the interface between the solid and the channels are retrieved from the ROM at every solver iteration. In this phase, different approaches to couple the high-fidelity solver to the low-order models may be considered (using a Schur-type or Schwarz-type method). For example, the POD coefficients of the ROMs may be evaluated by projecting the chamber solution on the interfaces between the two models in the subspace spanned by the POD modes. The solutions are recovered inside the ROM domains by prolongation of the solutions on the interfaces by using the POD modes. This allows in particular to recover the temperature or the heat flux to the channel wall and so to reconstruct a new set of boundary conditions for the high-fidelity solver. Such operation may have a reduced cost with respect to the iteration of the CFD solver.

[1] Buffoni, M., Telib, H., and Iollo, A. 2009. Iterative methods for model reduction by domain decomposition. Computers & Fluids.
[2] Iapichino, L., Quarteroni, A., and Rozza, G. 2012. A reduced basis hybrid method for the coupling of parametrized domains represented by fluidic networks. Computer Methods in Applied Mechanics and Engineering.
[3]Casenave, F., Akkari, N., Bordeu, F., Rey, C., and Ryckelynck, D. 2019. A Nonintrusive Distributed Reduced Order Modeling Framework for nonlinear structural mechanics - application to elastoviscoplastic computations. International Journal for Numerical Methods in Engineering. 
[4] Salmoiraghi, F., Scardigli, A., Telib, H., and Rozza, G. 2018. Free-form deformation, mesh morphing and reduced-order methods: enablers for efficient aerodynamic shape optimisation. International Journal of Computational Fluid Dynamics.


.. .. tabularcolumns:: |L|L|L|L|

.. table:: CT use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE CT02       |   Multi-physics coupling between a combustion chamber and cooling circuit channels  |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Spatial coupling between a reduced model and a high fidelity model in a           |
  |                     |   multi-physics problem                                                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   CPS, Mordicus                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   User with knowledge of the context and of the reduction modelling principles      |                                                        |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   User of a reduced-order model   | wants a reduced-order model coupled with a high |
  |                     |                                   | fidelity that behaves as the full-order one from|
  |                     |                                   | his point of view                               |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       |   From a high-fidelity calculation of the combustion chamber, the user provides a   | 
  |                     |   series of boundary conditions (the parameters) to be used for the training of the |
  |                     |   ROM.                                                                              |
  |                     |   The user computes the snapshots for a single channel model using the boundary     |
  |                     |   condition obtained in the previous step and the high fidelity solver.             |
  |                     |   The user prepare a very coarse mesh of the cooling circuit channels.              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  convergence of the coupled  multiphysics problem is obtained                       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  Calculation not completed                                                          |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  User enters the offline component of Mordicus while                                | 
  |                     |  announcing this particular use of the library                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | The user, in the offline phase, computes the POD bases that define the   |
  |                     |          | reduced space                                                            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | The user, in the online phase, determines the coefficients of the linear |
  |                     |          | combination of the global solution through the iterative procedure or    |
  |                     |          | with the Galerkin method on the reduced space (see above)                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1a       |  the user calculates a high fidelity solution on a (very) coarse mesh    |
  |                     |          |  over the entire domain of the cooling circuit channels to be added to   |
  |                     |          |  the reduced space                                                       |
  +---------------------+----------+------------------------+-------------------------------------------------+

