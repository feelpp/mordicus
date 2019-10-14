Cas n° CDM05
============
.. note::

   *Date*   : 03/03/2018


**Nom** : Cas test offline en déformations planes élastoplastiques sans base initiale

**Acteur(s)**   : Utilisateur 

**Description** : Un utilisateur calcul la solution EF d'un problème élasto-viscoplastique ainsi qu'une base réduite POD par POD incrémentale

Pré-conditions : Mise en donnée EF + demande de POD incrémentale

Démarrage : L'utilisateur lance la résolution du calcul EF

Description
-----------

Le scénario nominal
^^^^^^^^^^^^^^^^^^^
1. Initialisation du calcul EF (maillage, matériaux, ....)
2. A chaque incrément de temps enrichissement de la base POD par POD incrémentale
3. Stockage du nouveau mode POD calculé


Les scénarios d’exception
^^^^^^^^^^^^^^^^^^^^^^^^^
1.a 
  


COMPLEMENTS
-----------

Nécessite de pouvoir ajouter dans le format les modes d'une base réduite un par un. 
