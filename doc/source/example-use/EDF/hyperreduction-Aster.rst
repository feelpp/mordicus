.. _hyperreduction-Aster:

Exemple d'utilisation 2: réduction d'une étude mécanique avec Code_Aster
========================================================================

Contexte
--------

Ce cas d'usage est tiré d'un TP d'une formation dispensée par Mickaël Abbas.

L'utilisateur visé est un ingénieur R et D (au moins dans un premier temps), familier des lois de comportement plastiques, soit pour les métaux soit pour les sols, mais non spécialiste de la réduction de modèle. Cet ingénieur réalise des calculs utilisant des lois élasto-plastiques, sur des éprouvettes de structure non triviales (exemple cube de taille micro comportant plusieurs cristaux, ou colonne de sol hétérogène). Afin de valider ces calculs, il dispose de relevés expérimentaux sur des grandeurs globales de la structure. Il souhaitera donc utiliser la réduction de modèles dans un but de calibrage de paramètres matériaux locaux qui permettent le mieux de reproduire ces grandeurs globales.

Ici, nous prenons un exemple très simple d'une telle situation, à des fins de démonstration: la structure considérée pour l'éprouvette est une plaque trouée, la loi de comportement est élastoplastique à écrouissage isotrope suivant une loi puissance. Le cas nominal correspond au cas test de Code_Aster `FORMA03B <https://www.code-aster.org/V2/doc/default/fr/man_v/v6/v6.03.114.pdf>`_. La structure est présentée sur la figure :numref:`EDF_img3`. Une pression uniforme est appliquée sur la face supérieure, un quart de la structure est modélisé (des conditions de symétrie sont appliquées).

.. _EDF_img3:
.. figure:: img3.pdf

    Géométrie et chargement du cas simple considéré

Les paramètres variables (représentant les paramètres à calibrer) sont ceux de la loi de plasticité puissance.

La méthode utilisée est l'hyper-réduction par domaine d'intégration réduit, telle que proposée par D Ryckelynck `dans cet article <https://hal.archives-ouvertes.fr/hal-00359157/>`_ : une EIM est appliquée aux champs de contraintes nodaux. Les éléments finis entourant les noeuds retenus pour l'EIM constitue un domaine d'intégration réduit retenu pour la phase online, voir figure :numref:`EDF_img4`. Ce domaine d'intégration réduit doit contenir au moins un élément adjacent à la zone d'application de la pression pour que celle-ci soit prise en compte.


.. _EDF_img4:
.. figure:: img4.pdf

    Domaine d'intégration réduit généré

Formalisation de l'exemple d'utilisation
----------------------------------------

*Ici sous forme de liste*

:Nom: produire un calcul mécanique réduit avec Code_Aster (phase offline)

----

:Objectif (= intention principale du cas d’utilisation): Produire les éléments (à définir) qui permettront de faire tourner un modèle réduit.

----

:Acteur principal (= celui qui va réaliser le cas d’utilisation): le spécialiste "méthode numérique" de la méthode considérée. Appelé l’utilisateur

----

:Acteurs secondaires (= ceux qui reçoivent des informations à l’issue du cas d’utilisation): l’utilisateur métier de modèle réduit / le développeur de l’appli légère online.

----

:Système: dans ce cas, il s’agit d’une installation de Code_Aster

----

:Les pré-conditions (= état dans lequel le système doit être pour que le cas d’utilisation démarre): disposer d’une étude type mécanique, robuste sur la plage de paramètres visée.

----

:Scénario nominal (= échange d’évènements entre l’acteur et le système):

   * L’utilisateur exécute son étude N fois, pour N jeu de paramètres d’apprentissage dans la plage visée.

   * Le système produit N structures de données "résultat de type mécanique".

   * L’utilisateur rédige un jeu de données permettant de générer la base de modes empiriques. Il demande son exécution au système.

   * Le système génère cette base réduite, avec:

        - Données d’entrée:

            + Les structure de données "résultat de type mécanique"

            + Le nom symbolique des champs à considérer comme snapshots pour la construction des modes réduits

        - Algorithme:

            + Construction d’une matrice :math:`Q` temporaire par extraction des infos du résultat ;

            + snapshot POD codé en interne Fortran, sauf appel Lapack pour la SVD. Pas de "normalisation" de :math:`Q` par la matrice de masse ni de raideur : on fait directement une SVD de :math:`Q` et pas de :math:`\tilde Q`.

        - Données de sortie : une structure de données de type "résultat de type modes empiriques".

   * L’utilisateur rédige un jeu de données permettant de générer le Domaine d’Intégration Réduit (RID en anglais). Il demande son exécution au système.

   * Le système génère ce domaine d’intégration réduite, avec:

        - Données d’entrée:

            + Une structure de données "résultat de type modes empiriques", à la fois pour les températures et pour les flux aux nœuds

            + Une structure de données "maillage"

        - Algorithme : DEIM (Discrete Empirical Interpolation Method). Codé à la main en Fortran. Seule l’inversion d’une petite matrice pleine est faite avec Lapack.

        - Données de sortie : le maillage est enrichi avec:

            + Un groupe de mailles qui correspond au domaine d’intégration réduit (RID)

            + Un groupe de noeuds : les noeuds qui sont à considérer comme étant à la frontière du RID

    * L’utilisateur visualise le domaine d’intégration réduit. Il vérifie que pour chaque "zone de chargement" (zone du maillage où l’on applique un flux ou un terme source) est couverte par au moins un élément du domaine réduit. Sinon, on risque de "rater" des chargements dans le modèle hyper-réduit.

    * Si c’est le cas, l’utilisateur retourne à l’étape 5 en spécifiant un groupe de maille adjacent au chargement à inclure d’office dans le modèle réduit.

    * L’utilisateur définit une "étude réduite" sur le modèle de son étude type. L’étude réduite reprend tous les chargements et lois de comportement de l’étude type, mais ils sont définis sur le domaine d’intégration réduit et non plus sur la structure entière.

        - Exigence fonctionnelle : Ceci nécessite de trouver l’intersection de tous les groupes de mailles de définition des chargements avec celui définissant le domaine d’intégration réduit.

    * L’utilisateur demande au système l’exécution de son modèle réduit pour un jeu de paramètres qui se trouve dans la plage visée.

    * Le système lance l’opérateur de résolution sur l’étude réduite, avec:

        - Données d’entrée: 

            + maillage enrichi des infos sur le RID définie en 6, notamment les nœuds d’interface

            + base empirique de température à utiliser

            + information que l’étude est une "étude réduite" (autrement dit, que le système doit utiliser une résolution par hyper-réduction)

        - Algorithme : hyper-réduction. Principes d’implémentation généraux:

            + On utilise toute la tringlerie du solveur EF non-linéaire, notamment Newton-Raphson.
 
            + Seule différence avec une étude complète : seuls les noeuds du RID (intérieurs ou au bord) sont reconnus par le solveur comme faisant partie de la résolution.

            + On créé au début des structures de données pour différencier les noeuds intérieurs du RID des noeuds de bord.

            + On vient se brancher au niveau de l’étape de construction/résolution de chaque système linéaire à partir des vecteurs et matrices assemblés. On implémente l’algorithme d’hyper-réduction (résolution en coordonnées réduites des équations portées par les noeuds intérieurs) à cet endroit.
 
            + Les inconnues sont toujours associées à des DDL de Lagrange des éléments finis classiques. Il n’y a que dans cette routine spécifique de la réduction de modèles qu’on passe en coordonnées réduites. On reprojette en DDL classique avant la sortie de cette routine.

        - Données de sortie : structure de données "résultat de type mécanique réduit", mais qui ne contient les valeurs qu’en un petit nombre de noeuds. Cette structure de données contient la solution en coordonnées réduites.
 
    * Le système extrait les coordonnées réduites dans le résultat et les multiplie par les modes pour reconstruire un résultat complet : structure de données "résultat mécanique complet".

    * L’utilisateur confronte les résultats obtenus avec ceux de l’étude complète.

:Scénario alternatif: correction éléments finis.

.. todo::

    Rédiger les scénarios alternatifs et scénarios d'exception
