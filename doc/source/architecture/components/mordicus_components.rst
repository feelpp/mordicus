.. _mordicus_components:

Composants de Mordicus
----------------------


.. note::

   *Contributeurs* : participants à la réunion du 21/11/2018

   *Date*   : 22/11/2018


Générateur de données métier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : générer les données métier

**Input** : 

- source

- description méta-données métier

**Output** :

- données métier

- description méta-données métier

**Exemple** *source*: calcul, tomographie, photo, expérimentation; *description méta-données métier*: "u", "sigma", piquets de temps

Classificateur de données métier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : classifier les données métier

**Input** : 

- données métier

- description méta-données métier

**Output** :

- données métier regroupés par cluster

- description méta-données métier des éléments de chaque cluster




Extracteur de données métier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : extraire les données métier d'un cluster

**Input** : 

- liste de clusters

**Output** :

- données métier

- description méta-données métier



Compresseur de données métier
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : compresser les données métier

**Input** : 

- données métier

- description méta-données métier

**Output** :

- représentation compréssée des données métier

- description méta-données métier

**Exemple** : *représentation compréssée des données métier*: modes et coefficients, trains de tenseurs


Manipulateur de données métier compressées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Manipuler les données compressées

**Input** : 

- représentation compréssée des données métier

- description méta-données métier

**Output** :

- représentation compréssée des données métier

- description méta-données métier

**Exemple** :  interpoler, fusionner, orthonormaliser des bases


Visualisateur de données compressées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : visualiser les données compressées

**Input** : 

- données compréssées

**Output** :

- écran


Sérialisation de données compressées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : sauver les données compressées indépendamment du support, machine

**Input** : 

- données compressées

**Output** :

- fichiers, disques, cloud...


Compression des opérateurs
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Compresser les opérateurs pour garantir une construction efficace du modèle réduit

**Input** : 

- représentation compressée des données

- "modèle physique"

**Output** :

- représentation compressée des opérateurs sour forme d'une fonctionnelle "GetReducedOperator"

**Remarque** : *représentation compressée des opérateurs* contient optionnellement une évaluation efficace d'un estimateur ou indicateur d'erreur

Compression du terme source
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Compresser le terme source

**Input** : 

- "modèle physique"

**Output** :

- représentation compressée du terme source

**Exemple** : *terme source*: champ de pression sur un tag de surface, champ de température sur un tag de volume, effet centrifuge, débit d'entrée sur un tag de surface

**Remarque** : *terme source*: contient l'évolution temporelle

Résolution du problème réduit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Résoudre le problème réduit

**Input** : 

- représentation compressée des données métier

- représentation compressée du terme source

- représentation compressée des opérateurs

**Output** :

- représentation compressée de la solution du problème réduit





Reconstruction des quantités d'intérêt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Reconstruire les quantités d'intérêt

**Input** : 

- représentation compressée des données métier

- représentation compressée de la solution du probème réduit

- opérateur de la quantité d'intérêt

**Output** :

- quantité d'intérêt

**Exemple** : *opérateur de la quantité d'intérêt*: l'identité pour la solution complète, une forme linéaire de la solution


Evaluation de l'erreur
~~~~~~~~~~~~~~~~~~~~~~

**Objectif** : Evaluer l'erreur commise par le modèle réduit

**Input** : 

- représentation compressée des opérateurs

- quantité d'intérêt

**Output** :

- quantification de l'erreur


**Exemple** : *erreur*: estimateur d'erreur, indicateur d'erreur


REMARQUES
~~~~~~~~~

- les périphrases entre guillemet seront à préciser à la prochaine réunion

- fixer le vocabulaire/glossaire. Proposition: remplacer "données métier" par "snapshot" ou "solution" ou "champs physique" ?

- la séparation offline/online est volontairement absente: pour certaines méthodes, comme la méthode des bases réduites, ces notions sont mélangées

Summary of discussions from HK1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+----------------------+------------------------------------------------------------+
|**User environment**  | - User Data generation                                     |
+                      +------------------------------------------------------------+
|                      | - User Data classification                                 |
+                      +------------------------------------------------------------+
|                      | - User Data extraction                                     |
+                      +------------------------------------------------------------+
|                      | - User Data compression                                    |
+                      +------------------------------------------------------------+
|                      | - Compressed User Data manipulation                        |
+----------------------+------------------------------------------------------------+
|**Shared environment**| - Compressed data visualization                            |
+                      +------------------------------------------------------------+
|                      | - Compressed data serialization                            |
+----------------------+------------------------------------------------------------+
|                      | - Compression of operators                                 |
+                      +------------------------------------------------------------+
|                      | - Compression of sources                                   |
+                      +------------------------------------------------------------+
|    **MORDICUS**      | - Resolution of reduced problem                            |
+                      +------------------------------------------------------------+
|                      | - Reconstruction of interesting quantities                 |
+                      +------------------------------------------------------------+
|                      | - Error evaluation (algorithmic, verification, validation) |
+----------------------+------------------------------------------------------------+


**Remark:**

- **User environment** requiring specific treatment,  etc. algorithms, etc. should be defined and developed by partners.

- **Shared environment** includes data transfer, storage, visualization, etc.

- **MORDICUS contains** algorithms developed by all, communicates with **User environment** via APIs .


Non-intrusive process
~~~~~~~~~~~~~~~~~~~~~

1. **Non-intrusive typical process**

.. image:: img/non_intrusive_process.png
   :scale: 80 %
   :align: center

- :math:`X` = Model variables

- :math:`Y` = Model responses

- :math:`X_{new}` = Model new variables to predict

- :math:`Y_{new}` = Model new predicted responses

- :math:`C` = Coefficients

- :math:`F` = Basis function

2. **API Use cases**

- GUI

- Data exchange

- Super Elements

- Adaptive enrichment

Intrusive process
~~~~~~~~~~~~~~~~~

**To be defined**

This is the biggest unknown of the project at this stage. Should be discussed in order to ensure standard relevance for Hyper Reduction method.
