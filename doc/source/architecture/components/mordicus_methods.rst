.. _mordicus_methods:

Foreword
========

On imagine un problème à résoudre dans un domaine quelconque, dont un modèle prend la forme d'une équations aux dérivées partielles, dont l'inconnue est :math:`u (x, t; \mu )`:

.. math::
   :label: eq-meth-1

   f \left( x, t ; u( x, t; \mu ); \dfrac{\partial u}{\partial x_1}, ... \dfrac{\partial u}{\partial x_n}, \dfrac{\partial u}{\partial t}; \dfrac{\partial^2 u}{\partial x_1^2}, ...  \dfrac{\partial^2 u}{\partial x_1 t}, ... ; \mu \right)

où :math:`f` désigne une expression ou une procédure algébrique. Si :math:`f` est linéaire relativement au bloc :math:`\left(u, \dfrac{\partial u}{\partial x_1} ... \right)`, on dit que l'EDP est linéaire.

A partir des données métier, un solveur haute-fidélité écrire une discrétisation en espace de cette équation (une ODE donc), par une méthode de discrétisation de type éléments finis, volumes finis ou autre. :math:`u ( x, t; \mu)` est recherchée sous la forme d'une combinaison de fonctions polynomiales par morceaux, éventuellement discontinues entre les morceaux (cas des volumes finis et Galerkin discontinu):

.. math::
   :label: eq-meth-2

   u (x, t; \mu) = \sum_{k=0}^{\mathcal{N}} u_k (t; \mu) \phi_k ( x )

On introduit une discrétisation spatiale (un maillage) :math:`\mathcal{T} = \left\lbrace T_e \right\rbrace_{e=1}^E`, où :math:`T_e` désignent les éléments ou cellules deux à deux disjointes dont la réunion couvre le domaine :math:`\Omega`. Souvent, :math:`\phi_k` n'est non nul que sur petit sous-ensemble :math:`S(k)` d'éléments du maillage, de sorte que :numref:`eq-meth-2` peut se réécrire:

.. math::
   :label: eq-meth-3

   u (x, t; \mu) = \sum_{k=0}^{\mathcal{N}} u_k (t; \mu) \sum_{e \in S(k)} \phi_k^e ( x )

avec :math:`\phi_k^e ( x )` une fonction polynomiale, ou du moins une fraction rationnelle.

Dans certain cas, la variabilité agit sur la géométrie elle-même (celle -ci restant néanmoins fixe au cours du temps), et dans ce cas :math:`\phi_k` dépend de :math:`\mu`:

.. math::
   :label: eq-meth-4

   u (x, t; \mu) = \sum_{k=0}^{\mathcal{N}} u_k (t; \mu) \phi_k ( x; \mathbf{\mu})

Il se peut aussi que la résolution utilise une approche espace-temps, c'est-à-dire:

.. math::
   :label: eq-meth-5

   u (x, t; \mu) = \sum_{k=0}^{\mathcal{N}} u_k (\mu) \phi_k ( x, t)

On considère que cela ne sera pas le cas pour Mordicus pour la génération des snapshots.
  
Ces écritures :numref:`eq-meth-2`-:numref:`eq-meth-4` permettent la conversion de l'EDP :numref:`eq-meth-1` en une ODE:

.. math::
   :label: eq-meth-6

   F ( u, \dot{u}, ... u^{(m)}; t, \mu ) = 0

où cette fois :math:`u (t, \mu) = \left( u_k ( t; \mu) \right)_{1 \leq k \leq \mathcal{N}}`, et :math:`F` est une fonction ou une procédure algébrique. Si :math:`F` est linéaire relativement au bloc de variables :math:`( u, \dot{u}, ... u^{(m)})`, alors on dit que l'ODE est linéaire.

On introduit une discrétisation temporelle :math:`\left\lbrace t_i \right\rbrace_{i=0}^K`. Cette ODE :numref:`eq-meth-6` est en général résolue en utilisant un schéma différences finies en temps:

.. math::
   :label: eq-meth-7

   G_{n+1} (u_{n+1}; u_n, u_{n-1}, ...; \mu ) = 0

Si cette expression peut se réécrire sous une forme explicite en :math:`u_{n+1}`, le schéma est dit explicite en temps.

On définit alors la variété :math:`\mathcal{M}` des solutions discrètes comme:

.. math::
   :label: eq-meth-8

   \mathcal{M} = \left\lbrace u (t; \mu) : \mu \in \mathcal{P}, t \in \left\lbrace t_i \right\rbrace_{i=0}^K \right\rbrace

La réduction de modèle se base sur le constat qu'il est souvent possible de trouver un espace vectoriel :math:`\mathcal{Z}_N` ou une variété :math:`\mathcal{M}_N` de dimension :math:`N` faible proches de :math:`\mathcal{M}` (au sens d'indicateurs mathématiques type distance de Kolmogorov sur lesquels nous ne revenons pas ici), c'est à dire que la distance de tout point de :math:`\mathcal{M}` à :math:`\mathcal{M}_N` est faible.

La construction de :math:`\mathcal{Z}_N` (compression *linéaire*) ou :math:`\mathcal{M}_N` (compression *non-linéaire*) se fait avec un algorithme de *compression des données* à partir de solutions haute-fidélité :math:`\mathcal{S} = \left\lbrace u_k^i := u (t_i, \mu_k), 1 \leq i \leq K, \mu_k \in \mathcal{K} \right\rbrace`, dites snapshots, les :math:`\mu_k` sont pris dans un échantillonage :math:`\mathcal{K} = \left\lbrace \mu_1 , \cdots \mu_{N^{\mu}} \right\rbrace`.

.. note::

   Y a-t-il un intérêt à définir la variété des solutions continues ? Si oui lequel ?

Le *modèle réduit* du problème initial va rechercher une approximation de la solution dans :math:`\mathcal{Z}_N` ou :math:`\mathcal{M}_N`. C'est la phase de *résolution réduite*, pour laquelle on distingue deux grandes familles de méthodes:

   * les méthodes de *compression des opérateurs*: elles utilisent la connaissance du modèle physique: il s'agit de projeter :numref:`eq-meth-6` sur :math:`\mathcal{Z}_N` voir le réécrire en discrétisant :numref:`eq-meth-1` de façon appropriée sur :math:`\mathcal{Z}_N` ou :math:`\mathcal{M}_N`. Elles sont en général plus performantes en terle de qualité d'approximation et surtout nécessitent moins de *snapshots*. Elles sont néanmoins plus complexes à mettre en oeuvre, avec des spécificités qui dépendent du type de problème envisagé (elliptiques, paraboliques...)

   * les méthodes de *construction d'un méta-modèle*: elles n'utilisent pas les équations :numref:`eq-meth-6`, :numref:`eq-meth-1` du problème. Au lieu de cela, elles reposent sur des techniques de régression statistiques ou machine learning sur la seule donnée de :math:`\mathcal{S}`. Plus faciles à mettre en oeuvre, elles nécessitent plus de snapshots, pour une qualité d'approximation difficile à garantir.

Dans ces deux familles, certaines méthodes utilisent en plus des données de provenance expérimentales pour produire la solution réduite, on parle alors d'*assimilation de données*.

Ayant donné cette image générale, on peut dès à présent dresser une cartographie des méthodes dans les paragraphes suivants.

.. note::

   Donner uniquement l'algorithme pour chaque méthode, se contenter de citer des références pour les démonstrations


Compression des données
-----------------------

*Méthodes linéaires*

On construit une base réduite de :math:`\mathcal{Z}_N`, de sorte que :math:`\mathcal{Z}_N = Span \left\lbrace \zeta_n \right\rbrace_{n=1}^N`. On introduit la matrice des snapshots définis précédemment comme:

.. math::

   Q = \begin{bmatrix} u(t_1 , \mu_1) & \cdots & u(t_K , \mu_{N^{\mu}}) \\ \end{bmatrix} \in \mathbb{R}^{\mathcal{N} \times K N^{\mu}}

POD par SVD
~~~~~~~~~~~

On trouve alors les fonctions de base :math:`\left\lbrace \zeta_n \right\rbrace_{n=1}^N` comme les vecteurs singuliers dominants à gauche. On calcule la décomposition en valeurs singulières de :math:`Q`:

.. math::

   Q = U \Sigma V^T

avec:

.. math::

   \mathbb{R}_{M \times M} \ni \Sigma = \left( \sigma_1 , \cdots , \sigma_M \right) 

la matrice des valeurs singulières par ordre décroissant :math:`\sigma_1 > \cdots > \sigma_M \ge 0`, et :math:`M = \min \lbrace \mathcal{N} , K N^{\mu} \rbrace`. La base réduite est alors :math:`\zeta_i = U_i , i \in \mathbb{N} (N)`

*Prise en compte d'un opérateur de corrélation*

Appelons :math:`M` la matrice du produit scalaire par rapport auquel on souhaite compresser les données, et notons :math:`M = L L^T` sa décomposition de Choleski.

.. math::

   \tilde{Q} = L^T Q

On calcule sa décomposition en valeurs singulières:

.. math::

   \tilde{Q} = \tilde{U} \tilde{\Sigma} \tilde{V}^T

On obtient la matrice :math:`U` par:

.. math::

   U = L^{-T} \tilde{U}


.. rubric:: Références

.. bibliography:: ref-pod-svd.bib
  :all:
  :list: bullet

Snapshot POD
~~~~~~~~~~~~

On construit la matrice d'autocorrélation :math:`C \in \mathbb{R}^{K N^{\mu} \times K N^{\mu}}` des snapshots:

.. math::

    C_{ij} = \langle u(t_{k_i} , \mu_{l_i}) , u(t_{k_j} , \mu_{l_j})  \rangle

où :math:`\langle \bullet \rangle` est un produit scalaire d'intérêt pour les snapshots. On résoud le problème aux valeurs propres:

.. math::

    C \xi^i = \lambda^i \xi^i , i \in \mathbb{N}(K N^{\mu}) , \lambda_1 > \cdots > \lambda_{K N^{\mu}}

Les fonctions de base sont alors calculées comme:

.. math::

    \zeta_i = \dfrac{1}{\sqrt{\lambda_i}} \sum_{n=1}^{K N^{\mu}} \xi_n^i u(t_{k_n} , \mu_{l_n})

.. rubric:: Références

.. bibliography:: ref-snap-pod.bib
  :all:
  :list: bullet

Compression des opérateurs
--------------------------

*Work in progress*


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
    |                                       |  Sorbonne        |                               |                         |
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
    |                                       |  Sorbonne (1.1ef)| + For all:                    | reduced basis (built    |
    | NIRB                                  |                  |   fine solution vectors       | from fine mesh)         |
    | + Without Post treatment              |  EDF      (1.2h) |+ For rectification :          |                         |
    | + With rectification                  |                  |  coarse solution vector       |                         |
    | + Constrained minimization            |                  |                               |                         |
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
    |                                       |    Sorbonne      | scalar product of 2     |                             |
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
