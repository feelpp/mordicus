.. _hyperreduction-Aster:

=============================================================================
User story 1: réduction d'une étude thermique pour le soudage avec Code_Aster
=============================================================================

.. sous forme de liste de définition

:Nom: produire un calcul thermomécanique réduit avec Code_Aster (phase offline)

----

:Objectif (= intention principale du cas d’utilisation): Produire les éléments (à définir) qui permettront de faire tourner un modèle réduit.

----

:Acteur principal (= celui qui va réaliser le cas d’utilisation): le spécialiste « méthode numérique » de la méthode considérée. Appelé l’utilisateur

----

:Acteurs secondaires (= ceux qui reçoivent des informations à l’issue du cas d’utilisation): l’utilisateur métier de modèle réduit / le développeur de l’appli légère online.

----

:Système: dans ce cas, il s’agit d’une installation de Code_Aster

----

:Les pré-conditions (= état dans lequel le système doit être pour que le cas d’utilisation démarre): disposer d’une étude type thermique, robuste sur la plage de paramètres visée.

----

:Scénario nominal (= échange d’évènements entre l’acteur et le système):

   * L’utilisateur exécute son étude N fois, pour N set de paramètres d’apprentissage dans la plage visée.

   * Le système produit N structures de données « résultat de type thermique », telle que décrite dans la partie éléments techniques.

   * L’utilisateur rédige un jeu de données permettant de générer la base de modes empiriques, nous la forme. Il demande son exécution au système.

   * Le système génère cette base réduite, avec:

        - Données d’entrée:

            + Les structure de données « résultat de type thermique »

            + Le nom symbolique des champs à considérer comme snapshots pour la construction des modes réduits

        - Algorithme:

            + Construction d’une matrice Q temporaire par extraction des infos du résultat ;

            + POD codé en interne Fortran, sauf appel Lapack pour la SVD. Pas de « normalisation » de Q par la matrice de masse ni de raideur : on fait directement une SVD de Q et pas de :math:`\tilde Q`.

        - Données de sortie : une structure de données de type « résultat de type modes empiriques », telle que décrite dans la partie éléments techniques.

   * L’utilisateur rédige un jeu de données permettant de générer le Domaine d’Intégration Réduit (RID en anglais). Il demande son exécution au système.

   * Le système génère ce domaine d’intégration réduite, avec:

        - Données d’entrée:

            + Une structure de données « résultat de type modes empiriques », à la fois pour les températures et pour les flux aux nœuds

            + Une structure de données « maillage »

        - Algorithme : DEIM (Discrete Empirical Interpolation Method). Codée à la main en Fortran. Seule l’inversion d’une petite matrice pleine est faite avec Lapack.

        - Données de sortie : le maillage est enrichi avec:

            + Un groupe de mailles qui correspond au domaine d’intégration réduit (RID)

            + Un groupe de nœuds : les nœuds qui sont à considérer comme étant à la frontière du RID

    * L’utilisateur visualise le domaine d’intégration réduit. Il vérifie que pour chaque « zone de chargement » (zone du maillage où l’on applique un flux ou un terme source) est couverte par au moins un élément du domaine réduit. Sinon, on risque de « rater » des chargements dans le modèle hyper-réduit.

    * Si c’est le cas, l’utilisateur retourne à l’étape… en spécifiant un groupe de maille adjacent au chargement, à inclure d’office dans le modèle réduit.

    * L’utilisateur définit une « étude réduite » sur le modèle de son étude type. L’étude réduite reprend tous les chargements et lois de comportement de l’étude type, mais ils sont définis sur le domaine d’intégration réduit et non plus sur la structure entière.

        - Exigence fonctionnelle : Ceci nécessite de trouver l’intersection de tous les groupes de mailles de définition des chargements avec celui définissant le domaine d’intégration réduit.

    * L’utilisateur demande au système l’exécution de son modèle réduit pour un set de paramètre qui se trouve dans la plage visée, mais pas forcément un set d’apprentissage.

    * Le système lance l’opérateur de résolution sur l’étude réduite, avec:

        - Données d’entrée: 

            + maillage enrichi des infos sur le RID définie en …, notamment les nœuds d’interface

            + base empirique de température à utiliser

            + information que l’étude est une « étude réduite » (autrement dit, que le système doit utiliser une résolution par hyper-réduction)

        - Algorithme : hyper-réduction. Principes d’implémentation généraux:

            + On utilise toute la tringlerie du solveur EF non-linéaire, notamment Newton-Raphson.
 
            + Seule différence avec une étude complète : seuls les nœuds du RID (intérieurs ou au bord) sont reconnus par le solveur comme faisant partie de la résolution.

            + On créé au début des structures de données pour différencier les nœuds intérieurs du RID des nœuds de bord.

            + On vient se brancher au niveau de l’étape de construction/résolution de chaque système linéaire à partir des vecteurs et matrices assemblés. On implémente l’algorithme d’hyper-réduction (résolution en coordonnées réduites des équations portées par les nœuds intérieurs) à cet endroit.
 
            + Les inconnues sont toujours associées à des DDL de Lagrange des éléments finis classiques. Il n’y a que dans cette routine spécifique de la réduction de modèles qu’on passe en coordonnées réduites. On reprojette en DDL classique avant la sortie de cette routine.

        - Données de sortie : structure de données « résultat de type thermique réduit », mais qui ne contient les valeurs qu’en un petit nombre de nœuds. Cette structure de données contient la solution en coordonnées réduites.
 
    * Le système extrait les coordonnées réduites dans le résultat et les multiplie par les modes pour reconstruire un résultat complet : structure de données « résultat thermique complet ».

    * L’utilisateur confronte les résultats obtenus avec ceux de l’étude complète.

:Scénario alternatif: correction éléments finis.

.. todo::

    Rédiger les scénarios alternatifs et scénarios d'exception
