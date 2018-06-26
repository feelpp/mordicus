Cas n° CDM04
============
.. note::
   *Auteur* : Basile Marchand

   *Date*   : 03/03/2018


**Nom** : Permettre à l'utilisateur d'écrire ses informations *a priori* ayant servi à la construction du modèle 

**Acteur(s)**   : Utilisateur (calculateur)

**Description** : Un utilisateur doit pouvoir stocker toute information *a priori* étant nécessaire à la construction du modèle réduit, par exemple la matrice des snapshots. 

Pré-conditions : L'utilisateur vient de construire un modèle réduit et a déjà stocké ce dernier dans un fichier. Le fichier est déjà ouvert en écriture

Démarrage : L'utilisateur demande l'enregistrement des entrées de la construction du modèle réduit

Description
-----------

Le scénario nominal
^^^^^^^^^^^^^^^^^^^
1. Vérification de la non existence des informations dans le fichier
2. Enregistrement des informations a priori
3. Fermeture du fichier


Les scénarios d’exception
^^^^^^^^^^^^^^^^^^^^^^^^^
1.a Les informations ont déjà été sauvegardées
  Arrêt sur erreur.



COMPLEMENTS
-----------

Informations a priori :
* Matrice des snapshots pour POD like méthodes. 
* d'autres choses ? 
