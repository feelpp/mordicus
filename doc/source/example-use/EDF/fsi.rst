====================================================
Réduction de modèle sur un problème paramétrique IFS
====================================================

Motivation
==========

Ce use-case décrit la réduction de modèle au cas vibroacoustique (couplage IFS avec fluide stagnant, hypothèses acoustiques). Il permet de mettre en évidence l'importance de pouvoir traiter de manière séparée les composantes d'une solution selon leur nature physique. L'exemple traité ici est simple puisqu'il se contente de créer des modes empiriques spécialisés par composante. En particulier le nombre de modes total est :math:`n` fois celui demandé par l'utilisateur où :math:`n` est le nombre de groupe de composantes différents.

Une autre situation importante liée à cette fonctionnalité est le traitement des conditions limites (Dricihlet) par dualisation et donc emploi de multiplicateurs de Lagrange.
Par rapport à la situation précédente (IFS), on a aussi :math:`n=2` groupes de composantes mais le nombre de modes est différent entre ces deux groupes (les multiplicateurs de Lagrange reproduisant une condition linéaire, il faut moins de modes par exemple que pour les déplacements du problème non-linéaire)

Problème
========

Considérons un système physique dont la solution :math:`U(\alpha,x,t)` dépend du temps :math:`t`, de l'espace :math:`x` et des :math:`N_\alpha` paramètres :math:`\alpha_{i=1,N_{\alpha}}`. Ce système physique est solution de l'équation suivante:

:math:`\left( \sum_{r=1}^{n_r} C_r(\alpha_i) R_r \right ) \times U = \sum_{s=1}^{n_s} C_s(\alpha_i) S_s`

où :math:`R_r` sont des matrices (réelles ou complexes), :math:`C_r` sont les coefficients (réels ou complexes) devant chaque matrice, :math:`S_s` sont des vecteurs second membres (réels ou complexes) et :math:`C_s` sont des coefficients (réels ou complexes) devant chaque vecteur.

L'ensemble de ces coefficients :math:`C_r` et :math:`C_s` dépendant des :math:`N_\alpha` paramètres.

Par exemple, considérons l'EDO classique en dynamique des structures, sous forme paramétrée:

:math:`M (\alpha_{i}) \ddot U + C (\alpha_{i}) \dot U + K (\alpha_{i}) U = F (\alpha_{i})`

On suppose qu'on a été capable d'en écrire une version purement affine (par exemple par une EIM):

:math:`C_m(\alpha_i) M \ddot U + C_c(\alpha_i) C \dot U + C_k(\alpha_i) K U = C_f(\alpha_i) F`

La principale caractéristique de ce problème c'est que le vecteur solution :math:'U' est composé de plusieurs composantes physiques de nature différente. Par exemple, une formulation à trois composantes avec le déplacement, la pression et le potentiel de vitesse.

Pour construire une base réduite :math:`\Phi`, il est nécessaire qu'elle respecte certaines conditions pour garantir la stabilité de la solution après discrétisation temporelle (par un schéma de Newmark par exemple). La base est classiquement construite par un algorithme glouton.

Le système est de taille :math:`N_eq` (avec :math:`N_eq` possiblement grand, issu d'un calcul EF). Les matrices sont donc de dimension :math:`N_eq \times N_eq` et les vecteurs (seconds membres et solution) sont de dimension  :math:`N_eq` . Le vecteur solution :math:`U` contient trois sous ensembles de coefficients, groupés suivant le type de degré de liberté (ici, déplacement, pression et potentiel de vitesse). L'ordre de ces coefficients dépend bien entendu de la numérotation globale du problème et doit être cohérent avec la numérotation des matrices et vecteurs seconds membres.


Données d'entrée
================

L'utilisateur va fournir:

* L'ensemble des matrices :math:`R_{r=1,n_r}` et des seconds membres :math:`S_{s=1,n_s}` de son problème 
* Un ensemble d'entraînement des paramètres :math:`\alpha_{i=1,N_{\alpha}^t}^t`
* L'expression des coefficients :math:`C_r` et :math:`C_s` en fonction des paramètres
* Des critères de convergence pour l'algorithme glouton: nombre de modes et/ou tolérance

Algorithme
==========

Initialisation (calcul du premier mode)
---------------------------------------

* Calcul des coefficients initiaux :math:`C_r^0` et :math:`C_s^0`  (première évaluation à partir de l'ensemble d'entraînement des paramètres)
* Évaluation du second membre initial :math:`\sum_{s=1}^{n_s} C_s^0(\alpha_i) S_s` (il n'y a que les coefficients qui varient)
* Évaluation du premier membre initial :math:`\sum_{r=1}^{n_r} C_r^0(\alpha_i) R_r` (il n'y a que les coefficients qui varient)
* Résolution du système initial pour trouver :math:`U^0` (cette résolution se fait donc sur le système complet)
* Séparation de la solution en trois solutions sur les trois composantes distinctes :math:`U^0 \rightarrow (U_1^0,U_2^0,U_3^0)`. cette séparation se fait sur la base suivante:
    - Le vecteur U_1 est de dimension :math:`N_eq` mais a des composantes non nulles uniquement pour le premier groupe de degrés de liberté (par exemple: le déplacement). Le reste est constitué de zéros
    - Le vecteur U_2 est de dimension :math:`N_eq` mais a des composantes non nulles uniquement pour le deuxième groupe de degrés de liberté (par exemple: la pression). Le reste est constitué de zéros
    - Le vecteur U_3 est de dimension :math:`N_eq` mais a des composantes non nulles uniquement pour le troisième groupe de degrés de liberté (par exemple: le potentiel de vitesse). Le reste est constitué de zéros
* Normalisation des vecteurs solutions :math:`(U_1^0,U_2^0,U_3^0)` (unitaire)
* Eventuelle ré-orthogonalisation des vecteurs solutions (algorithme MGS)

Ces trois premiers vecteurs solutions sont les trois premiers modes de la base réduite.

Algorithme greedy
-----------------

* On initialise :math:`t \leftarrow t_0`
* Boucle sur les modes (tant que le nombre de modes est inférieure à la valeur données par l'utilisateur). A noter qu'il faut multiplier par trois cette valeur utilisateur puisqu'on aura trois modes propres à chaque fois.
    - Calcul des coefficients courants :math:`C_r^t` et :math:`C_s^t` pour le jeu :math:`t` de paramètres
    - Calcul du résidu pour glouton (classiquement par écart entre la solution réelle et celle reconstruite par ROM pour tout l'ensemble dest paramètres d'entraînement)
    - Récupération de la valeur maximale du résidu et de l'indice du paramètre :math:`t_maxi` réalisant ce maximum
    - Si cette valeur maximale est inférieure à la tolérance => BREAK
    - Calcul du second membre avec le paramètre d'entraînement maximum
    - Calcul du premier membre avec le paramètre d'entraînement maximum
    - Résolution du système pour trouver :math:`U^t_maxi` (cette résolution se fait donc sur le système complet)
    - On a :math:`t \leftarrow t_maxi` 
    - Normalisation des vecteurs solutions :math:`(U_1^t,U_2^t,U_3^t)` (unitaire)
    - Eventuelle ré-orthogonalisation des vecteurs solutions (algorithme MGS)
    - Trois nouveaux modes
* Fin de la boucle sur les modes

C'est un algorithme glouton classique, la seule différence est que les modes empiriques sont séparés par type de composante dans le vecteur des inconnues. On démontre qu'une telle construction produit une base empirique stable pour le schéma en temps utilisé.



