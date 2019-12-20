.. _linear-thermics-MAP:

Exemple d'utilisation 1: réduction d'un calcul thermique linéaire instationnaire
================================================================================


Contexte
--------

L’utilisateur est un ingénieur R et D mettant au point puis réalisant des études avancées de robinetterie. Ces études sont volumineuses (1 M DDL), longues et complexes. L’étude "nominale" est sauvegardée dans un outil de capitalisation. Il est familier de l’utilisation d’un code de calcul thermo-mécanique, mais n’est pas développeur. Il a une connaissance avancée de la méthode des éléments finis, des modélisations thermiques et des composants (clapet, pompe) qu’il modélise. Il connaît le principe général de la réduction de modèles, sans en maîtriser les algorithmes. Il utilise python pour manipuler des résultats de simulation, ne connaît pas d’autre langage de programmation. 

Dans cet exemple d'utilisation (tiré d'un TP de formation donnée par Amina Benaceur), l’utilisateur souhaite, à partir d’une étude "nominale" de thermique non linéaire instationnaire d'un clapet, faire réaliser une étude de sensibilité à des coefficients d’échange incertains. L'objectif à terme est d'évaluer l'influence sur les contraintes générées par la dilatation thermique. Pour cela, son objectif est de produire une structure de donnée autonome qui permettra de réaliser un calcul très rapidement, en tant que module d’une plateforme de capitalisation ergonomique.

La géométrie du clapet a été reconstituée conformément aux nuages de points obtenus par relevés 3D de la peau externe. La peau interne a été construite daprès un plan prêté par le constructeur. Un
maillage, réglé dans la mesure du possible, a été construit à partir de cette géométrie. L’ensemble du modèle, constitué déléments linéaires, comprend environ 121 000 noeuds. Par contre, le chargement
thermique respecte cla symétrie XOY de la pièce, les calculs de contraintes thermiques sont donc faits sur un demi maillage.

.. _EDF_img1:
.. figure:: img1.pdf

    Vue d'ensemble du demi-modèle de clapet

L'étude nominale consiste à trouver l'évolution de la température dans la structure, supposée avoir une conductivité :math:`\lambda` et une capacité calorifique :math:`\rho c_P` constantes. Les échanges de chaleur entre fluide et paroi interne, d’une part, entre paroi externe et air ambiant, d’autre part, sont modélisés chacun par une équation de flux de Newton :math:`-\lambda \nabla T \cdot \mathbf{n} = h ( T - T_f )`, où :math:`\mathbf{n}` est la normale à la paroi, :math:`T` la température du solide en paroi, sur laquelle s’exerce la condition aux limites, :math:`T_f` la température caractéristique du fluide, qui est une fonction donnée du temps pour le fluide interne et 20 degrès pour les parois externes. Les zones d'échange applicables en peau interne sont présentées en :numref:`EDF_img2`. Les paramètres variables peuvent être :math:`h` ou :math:`lambda`.

La méthode de réduction utilisée a été développée dans `la thèse d'Amina Benaceur <https://hal.archives-ouvertes.fr/tel-01958278v2/document>`_. Pour le cas linéaire, il s'agit d'un simple POD sur les calculs complets pour obtenir une base réduite, suivie d'une projection de Galerkin des opérateurs du problème sur cet espace réduit. La résolution online est entièrement codée en python, hors de Code_Aster, avec un schéma d'Euler implicite. La méthode de réduction est appliquée à travers une plateforme de simulation.


.. _EDF_img2:
.. figure:: img2.pdf

    Zones d'application des coefficients d'échange thermique

Références ouvertes: 

   * description de la méthode https://hal.archives-ouvertes.fr/tel-01958278v2/document

   * description du cas https://hal.archives-ouvertes.fr/hal-01599304v4/document

 
.. todo::

   Ce cas d'usage est le plus simple parmi ceux développés dans ce cadre pour la thermique. On trouvera également dans ces références des méthodes EIM appliquée de manière gloutonne (réduisant ainsi le coût de la phase *offline*) pour la réduction de problèmes de thermique non-linéaire. Des cas d'usage plus élaborés en thermique non linéaire devront être rédigés.


Formalisation de l'exemple d'utilisation
----------------------------------------


.. sous forme de liste de définition

:Nom: produire un calcul thermique linéaire instationnaire réduit

----

:Objectif (= intention principale du cas d’utilisation): Produire les éléments qui permettront de faire tourner un modèle réduit.

----

:Acteur principal (= celui qui va réaliser le cas d’utilisation): le spécialiste « méthode numérique » de la méthode considérée. Appelé l’utilisateur

----

:Acteurs secondaires (= ceux qui reçoivent des informations à l’issue du cas d’utilisation): l’utilisateur métier de modèle réduit / le développeur de l’appli légère online.

----

:Système: dans ce cas, il s'agit à la fois d'une installation de Code_Aster et d'une installation de la plateforme de capitalisation MAP, à remplacer par Mordicus dans le futur

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

            - un résultat (n'importe lequel) de la phase *offline* de 2. Permet de récupérer (i) le maillage et (ii) la liste d'instants (ce qui n'est pas très sain)

        * Algo:

            - marche en temps avec les opérateurs réduits

            - reprojection des résultats sur le maillage

        * Données de sortie:

            - un résultat MED par valeur de paramètre, comme en 2.
