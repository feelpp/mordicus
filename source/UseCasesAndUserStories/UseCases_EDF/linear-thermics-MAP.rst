.. _linear-thermics-MAP:

=========================================================================
User story 2: réduction d'un calcul thermique linéaire instationnaire MAP
=========================================================================

.. sous forme de liste de définition

:Nom: produire un calcul thermique linéaire instationnaire réduit avec MAP

----

:Objectif (= intention principale du cas d’utilisation): Produire les éléments (dans MAP) qui permettront de faire tourner un modèle réduit.

----

:Acteur principal (= celui qui va réaliser le cas d’utilisation): le spécialiste « méthode numérique » de la méthode considérée. Appelé l’utilisateur

----

:Acteurs secondaires (= ceux qui reçoivent des informations à l’issue du cas d’utilisation): l’utilisateur métier de modèle réduit / le développeur de l’appli légère online.

----

:Système: dans ce cas, il s'agit à la fois d'une installation ed Code_Aster et d'une installation MAP

----

:Les pré-conditions (= état dans lequel le système doit être pour que le cas d’utilisation démarre): disposer d’une étude type thermique instationnaire linéaire dans Code_Aster, robuste sur la plage de paramètres visée.

----

:Scénario nominal (= échange d’évènements entre l’acteur et le système):

    #. L'utilisateur lance une version paramétrique de son étude. Note: le paramètre est défini par une variable python dans le jeu de commande et ses valeurs dans un fichier à part.

    #. Le système "Code_Aster" produit les résultats (format MED) dans des dossiers: un dossier par valeur de paramètre, dans l'ordre de définition de ces paramètres.

    #. L'utilisateur lance un jeu de commandes permettant d'exporter les opérateurs du calcul éléments finis.

    #. Le système "Code_Aster" produit ces opérateurs.

        * Données de sortie = matrices au format numpy compressé (npz)

            - matrice de capacité C

            - matrice de conductivité K

            - une matrice :math:`B_i` par condition au limites d'échange


    #. L'utilisateur définit la phase *offline* dans MAP. Il exécute MAP.

    #. Le système "MAP" réalise la phase *offline*:

        * Données d'entrée:
        
            - les résultats MED de 2.

            - les opérateurs haute-fidélité de 4.

            - une tolérance, critère de troncature, pourcentage de l'énergie qu'on accepte de perdre dans la construction de la base réduite

            - faut-il construire le modèle réduit au format MED ou npz?

            - "le reste des informations nécessaires à la construction du modèle réduit". Dans notre cas, il s'agit de:

               * la capacité (qui n'est pas un paramètre variable);

               * les coefficients d'échange et températures extérieures au cours du temps, sous forme de fichiers CSV "avec des conventions implicites": la première colonne est le temps, puis 2 colonnes par zones d'échanges dans un ordre qu'on a convenu.

        * Algo: progressive RB = algo glouton qui ne nécessite des SVD qu'en dimension réduite

        * Données de sortie : le modèle réduit (!!) sous formes de matrices et vecteurs numpy compressés (npz):

            - la base réduite;

            - le vecteur de la condition initiale en coordonnées réduite;

            - les opérateurs de 4. projetés sur la base réduite;

            - les conditions aux limites de Dirichlet (champs de température extérieure) en coordonnées réduites;

            - les termes sources en coordonnées réduites.

    #. L'utilisateur teste le modèle réduit dans MAP (phase *online*) et exécute

    #. Le système MAP réalise la phase *online*

        * Données d'entrée:

            - le modèle réduit (base réduite et opérateurs projetés) de 6.

            - le "reste des informations du modèle" tel que défini en 6. (à discuter)

            - la liste des valeurs de paramètres à tester

            - un résultat (n'importe lequel) de la phase *offline* de 2. Permet de récupérer (i) le maillage et (ii) la liste d'instants (ce qui n'est pas très sain.
        * Algo:

            - marche en temps avec les opérateurs réduits

            - reprojection des résultats sur le maillage

        * Données de sortie:

            - un résultat MED par valeur de paramètre, comme en 2.
