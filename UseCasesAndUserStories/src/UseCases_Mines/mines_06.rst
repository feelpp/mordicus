Cas n° CDM06
============
.. note::

   *Date*   : 03/04/2018


**Nom** : Cas test online en déformations planes élastoplastiques sans base initiale

**Acteur(s)**   : Utilisateur 

**Description** : Un utilisateur calcul la solution EF d'un problème élasto-viscoplastique à l'aide d'une base réduite de type POD sur un maillage réduit 

Pré-conditions : Mise en donnée EF (Cond Lim, Mat, ...) + Mise en donnée ROM 

Démarrage : L'utilisateur lance la résolution du calcul EF ROM

Description
-----------

Le scénario nominal
^^^^^^^^^^^^^^^^^^^
1. Initialisation du calcul EF (maillage, matériaux, ....) en ne considérant que le maillage réduit
2. Chargement de la base réduite de DOF et en option la base réduite de FLUX (pour l'estimation d'erreur)
3. A chaque incrément résolution Hyper Réduite
4. A chaque incrément stockage : (i) du champ solution EF sur le maillage réduit ; (ii) des coordonnées réduites en DOF (et FLUX si nécessaire)


Les scénarios d’exception
^^^^^^^^^^^^^^^^^^^^^^^^^
1.a 
  

COMPLEMENTS
-----------

Nécessite d'avoir plusieurs type de base, des bases sur les DOFS et des bases sur des variables integ

Il faut pour chaque base être à même d'identifier sur quelle quantité elle porte.

