.. _UC_Safran01:

Safran Use Case
---------------


The use case has been published:
Casenave, F., Akkari N., Bordeu F., Rey C., Ryckelynck D. (2020). A Nonintrusive Distributed Reduced Order Modeling Framework for nonlinear structural mechanics -- application to elastoviscoplastic computations, International Journal for Numerical Methods in Engineering 121, 32-53, https://doi.org/10.1002/nme.6187, `available on arxiv <https://arxiv.org/abs/1812.07228>`_.

A performance race is currently underway in the aircraft engine industry. The materials of some
critical parts of the engine are pushed to the limit of their strength to increase as much as possible the
efficiency of the propulsion. In particular, the high-pressure turbine blades, which are located directly
downstream from the chamber of combustion, undergo extreme thermal loading. The possible causes
of failure for these turbines include temperature creep rupture and high-cycle fatigue. Many
efforts are spent to increase the strength of these turbines, with the use of thermal barriers, advanced superalloys and complex internal cooling channels.
The lifetime prediction of such complex parts is a very demanding
computational task: the meshes are very large to account for small structures such as the cooling
channels, the constitutive laws are strongly nonlinear and involve a large number of internal variables,
and more importantly, a large number of cycles has to be simulated. Indeed, failures come from local structural effects whose evolution cannot be predicted without computing potentially hundreds of
cycles.
Like the lifetime prediction of turbine blades, many industrial needs involve very intensive numerical procedures, where the approximations of partial differential equations are solved. Efforts are
spent to mitigate the runtime issues. In the context of nonlinear structural mechanics, we consider
the conjugation of parallel computing with distributed memory to accelerate the resolution of large
problems with Reduced Order Modeling, which learns about the physical operators from a solution
set computed beforehand to accelerate further computations.

The use case consisite in reducing nonlinear structural mechanics problems in a nonintrusive fashion.
The framework uses different algorithms taken from the literature and employs them to treat large
scale problems. All the computation procedure is parallel with distributed memory: the computation
of the high-fidelity model, the reduction routines using in-house distributed python routines, up to
the visualization and post-treatment. The nonintrusivity feature is obtained by having coded all
the finite-element operation needed in a posteriori reduced order modeling procedure in the library mor_dicus.



.. .. tabularcolumns:: |L|L|L|L|

.. table:: Safran use case
  :class: longtable

  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Safran01   |   Acc??l??rer un calcul cyclique elasto-visco-plastique d???aube de turbine             |
  |                     |   haute pression                                                                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Evaluer efficacement la dur??e de vie d???une aube de tubine haute-pression          |
  |                     |   en r??gime elastoviscoplastique                                                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   The offline and online component of Mordicus library                              |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |   Primary task                                                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   Concepteur / designer                                                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |   User of a reduced-order model   | wants a reduced-order model that behaves as     |
  |                     |                                   | the full-order one from his point of view       |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       | Avec recalcul des snapshots:                                                        |
  |                     |                                                                                     |
  |                     |     - Une mise en donn??e Z-set pour le calcul haute-fid??lit?? (?? recalculer)         |
  |                     |                                                                                     |
  |                     | En mode non intrusif:                                                               |
  |                     |                                                                                     |
  |                     |     - Une mise en donn??e pour le calcul haute-fid??lit?? (pour avoir le chargement)   |
  |                     |                                                                                     |
  |                     |     - Des snapshots pr??calcul??s                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  Un calcul cyclique extrapol?? par mod??le r??duit                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  Calcul non abouti                                                                  |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  User enters the offline component of Mordicus while                                | 
  |                     |  announcing this particular use of the library                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | L???utilisateur fourni un mise en donn??es Z-set de son calcul EVP          |
  |                     |          | d???aube de turbine haute pression                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | L???utilisateur remplit un fichier de param??tres pour les diff??rentes      |
  |                     |          | options disponibles (pour data compression, operator compression,        |
  |                     |          | reconstruction des quantit??s duales, nonintrusivit??,                     |
  |                     |          | nombre de cycles ?? extrapoler)                                           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | Les phases offline, online, la reconstruction des quantit??s duales       |
  |                     |          | sont cha??n??s automatiquement sur une architecture HPC                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | Pas d?????l??ments de robustification du code                                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Related information |          | N??cessite une licence ZMat pour ??x??cuter le ROM                          |
  +---------------------+----------+------------------------+-------------------------------------------------+

