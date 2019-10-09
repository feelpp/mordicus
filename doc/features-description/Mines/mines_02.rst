Cas n° CDM02
============
.. note::
   *Auteur* : Basile Marchand

   *Date*   : 03/03/2018


**Nom** : Fournir à l'utilisateur les caractéristique du modèle réduit

**Acteur(s)**   : Utilisateur 

**Description** : Un utilisateur doit pouvoir récupérer les informations minimales nécessaire à l'interprétation du modèle réduit stocké.

Pré-conditions : None

Démarrage : L'utilisateur demande les informations descriptives du modèle réduit stocké dans le fichier `rom_file`

Description
-----------

Le scénario nominal
^^^^^^^^^^^^^^^^^^^
1. Vérification de l'existence du fichier
2. Ouverture du fichier
3. Chargement des informations de description du modèle réduit
4. Retour à l'utilisateur de la description


Les scénarios d’exception
^^^^^^^^^^^^^^^^^^^^^^^^^
1.a Le fichier n'existe pas. 
  Un message d'erreur est envoyé à l'utilisateur


COMPLEMENTS
-----------

Quel structure pour le retour utilisateur ? 

Dépend du modèle réduit : 

- PGD  

    * Nombre de modes

    * Décomposition considérée (paramétrage)

    * La discrétisation de chaque dimension

- Hyper Réduction 

