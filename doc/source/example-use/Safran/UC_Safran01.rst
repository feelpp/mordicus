.. _UC_Safran01:

Safran Use Case
---------------

*Contexte à ajouter*

.. .. tabularcolumns:: |L|L|L|L|

.. table:: Safran use case
  :class: longtable

  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE Safran01   |   Accélérer un calcul cyclique elasto-visco-plastique d’aube de turbine             |
  |                     |   haute pression                                                                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Evaluer efficacement la durée de vie d’une aube de tubine haute-pression          |
  |                     |   en régime elastoviscoplastique                                                    |
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
  |                     |     - Une mise en donnée Z-set pour le calcul haute-fidélité (à recalculer)         |
  |                     |                                                                                     |
  |                     | En mode non intrusif:                                                               |
  |                     |                                                                                     |
  |                     |     - Une mise en donnée pour le calcul haute-fidélité (pour avoir le chargement)   |
  |                     |                                                                                     |
  |                     |     - Des snapshots précalculés                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  Un calcul cyclique extrapolé par modèle réduit                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  Calcul non abouti                                                                  |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  User enters the offline component of Mordicus while                                | 
  |                     |  announcing this particular use of the library                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | L’utilisateur fourni un mise en données Z-set de son calcul EVP          |
  |                     |          | d’aube de turbine haute pression                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | L’utilisateur remplit un fichier de paramètres pour les différentes      |
  |                     |          | options disponibles (pour data compression, operator compression,        |
  |                     |          | reconstruction des quantités duales, nonintrusivité,                     |
  |                     |          | nombre de cycles à extrapoler)                                           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | Les phases offline, online, la reconstruction des quantités duales       |
  |                     |          | sont chaînés automatiquement sur une architecture HPC                    |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | Pas d’éléments de robustification du code                                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Related information |          | Nécessite une licence ZMat pour éxécuter le ROM                          |
  +---------------------+----------+------------------------+-------------------------------------------------+

