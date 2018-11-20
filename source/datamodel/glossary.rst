.. _glossary:

Glossaire
---------

A lire chronologiquement (idéalement).

.. glossary::

    CAS_A_RESOUDRE
        Question d'intérêt à résoudre dans un domaine quelconque (définition du *Larousse*), par un raisonnement scientifique traduisible en équations. On parle aussi de *problème*.
        
    SOLVEUR
        Ensemble d'opérations permettant la traduction en équations du problème à partir d'informations "de plus haut niveau", puis sa résolution. Il prend la forme d'un logiciel.

    SOLVEUR_HF
        Solveur développé et utilisé par les spécialistes du domaine considéré, préexistant à la tâche de réduction de modèles.

        Caractéristiques: Peut fonctionner sur des problèmes de grandes taille, à condition d'avoir des calculateurs appropriés. Difficile d'analyser les algorithmes mis en oeuvre autrement que par la documentation. Précis mais long. Code source volumineux et **peu ou pas modifiable**.

    DONNEES_DU_PROBLEME
        Informations "de haut niveau" définissant un cas à résoudre, utilisables par le solveur HF pour traduire le problème en équations.

        :Questions: 

             Parle-t-on uniquement de la définition du problème continu ou également du problème discret?

             Autrement dit, regroupe-t-on sous ce vocabulaire toutes les données nécessaires à l'exécution d'un solveur HF?

             Faut-il distinguer entre (i) données de définition du problème **continu** (mise en données), (ii) options de discrétisation en espace ou en temps, (iii) options de résolution algébriques (traitement des conditions de Dirichlet, solveur linéaire...), (iv) options d'exécution (version du code, serveur etc).
 
        Caractéristiques: ces données sont fournies au solveur sous une forme codifiée, le code dépendant du solveur.

    DONNEES_FIXES
        Données considérées pour la question d'intérêt comme invariantes, soient parce que suffisamment bien connues soit parce que peu influentes sur les résultats d'intérêt.  

    DONNEES_VARIABLES
        Données considérées pour la question d'intérêt comme variables. On parle aussi de **paramètres**. Un cas possèdant des données variables est dit **paramétrique**. Une première information permet de savoir où elles s'insèrent dans la mise en donnée du problème **continu**. Cela prend la forme d'un identifiant repris dans la mise en données du problème. Une seconde information est le domaine de variation admissible. Optionnel: ensemble discret de valeurs à balayer, valeurs effectivement balayées.

    EDP
        Les équations continues correspondant au cas à résoudre.

    SUPPORT_SNAPSHOT
        Ensemble d'entités géométriques (points, arêtes, faces, volumes...) sur lesquelles s'appuient à la fois la définition du problème et sa traduction en équations. SUPPORT_SNAPSHOT est une généralisation de MAILLAGE qui permet d'inclure les méthodes à géométrie variable et d'autres use cases particulier (neutronique).

        Caractéristiques: Souvent de nature discrète (maillage) et de grande taille

        Exemples: points, arêtes, faces, volumes et ensemble les regroupant (maillage ou CAO)

        Questions: inclut-on également l'élément de référence et les fonctions de forme en EF? Parle-t-on du problème discret (maillage) ou continu (CAO)?

    MAILLAGE
        Spécialisation de SUPPORT_SNAPSHOT, c'est une discrétisation spaciale d'un milieu continu pouvant être directement utilisée par les méthodes numériques de résolution d'EDP communes: éléments finis ou volumes finis. Il s'agit d'un ensemble de cellules (ou encore éléments) dont l'intersection mutuelle est soit vide, soit une seul point, soit une arête, soit une face.

        Questions: les éléments qui constituent un maillage restent à définir plus précisément.

    SOLUTION_CAS ou SNAPSHOT
        Valeur d'une quantité mathématique pour laquelle le système d'équations **discret** est satisfait (*Larousse*), pour une valeur de paramètre donnée, temps **inclus**. Une solution se rapporte, via son cas et éventuellement sa valeur de paramètre, à un support géométrique de type SUPPORT_SNAPSHOT. Une SOLUTION_CAS contient une **clé** (INDEXATION) permettant de repérer la valeur de paramètre à laquelle elle se rapporte, et une **valeur** (attribut *field*).

        Caractéristique: la *quantité mathématique* en question est souvent un *vecteur*. On parle souvent de *snapshot* en réduction de modèles.

    COLLECTION_SOLUTION_CAS
        Ensemble de solutions, chacune étant qualifée par sa valeur des données variables (temps inclus), parmi les valeurs effectivement balayées.

        Caractéristique: souvent utilisée par les algorithme sous forme d'une matrice :math:`Q`, dite *matrice des snapshots*.

    DOMAINE_INTEGRATION_REDUIT
        Filtre sur un SUPPORT_SNAPSHOT, permettant de sélectionner des entités géométriques d'intérêt pour la construction d'opérateurs compressés.
        
        Caractéristique: souvent de petite taille.

        Exemple: points d'intégrations empiriques (NUAGE_DE_POINTS), éléments finis d'une hyper-réduction (SOUS_DOMAINE_DE_CALCUL_REDUIT)

    OPERATEUR_DE_CONSTRUCTION
        Toute donnée de nature non géométrique ou toute procédure utile à la traduction en équations **discrètes** du problème. Ce sont des "prises" ajustables complétant (le plus souvent) ou modifiant (plus rarement) l'ensemble d'opérations du solveur.

        Exemples: poids du schéma de quadrature, matrices et vecteurs précalculés, routine de comportement, fonctions de calcul des quantités duales, procédures de reconstruction du gradient, procédures d'assemblage particulières etc.

        Caractéristique: on peut imaginer qu'un certain nombre d'opérateurs de construction "classiques" soient présents dans l'implémentation par défaut. Certains opérateurs de constructions simples reposent sur des projections (produits matrices/vecteurs) à partir de matrices et vecteurs précalculées par un solveur HF. Ils doivent pouvoir être appelés depuis un calcul *complet* ou *réduit*.

        Questions: a priori, inclut également les routines permettant la traduction en équations du problème réduit à partir des coordonnées réduites? (Hypperreduction.ComputeReducedInternalForces et Hyperreduction.ComputeReducedGlobalTangentMatrix)? Faut-il distinguer donnée et procédure dans le modèle de données? Est-ce qu'on inclut les donnée ou procédure utile non pas à la traduction en équations, ms à la résolution algébrique? Classe dérivée "OPERATEUR_DE_PROJECTION"? Faire apparaître les matrices et vecteurs précalculés et l'entité informatique responsable de ce pré-calcul?

    METHODE_DE_REDUCTION
        Opérations de la phase *offline* permettant la définition d'un petit nombre de fonctions de l'espace, dites "fonctions de bases", servant à la définition d'un espace réduit de recherche de la solution. Elle produit une collection de solutions, laquelle est tagguée (comment?) comme "base réduite".

        Question: expliquer pourquoi ce n'est pas équivalent à dire "opérations de la phase *offline* n'impliquant pas de domaine de calcul réduit"? Elle s'appuie sur la matrice des snapshots indépendamment du problème?

    OPERATEUR_DE_COMPRESSION
        Opérations de la phase *offline* ayant pour but la production des opérateurs de construction d'un modèle réduit ou la diminution de leur complexité algorithmique (dans le but d'accélérer la phase *online*). Il produit des opérateurs de construction réduits.

        Caractéristique: il peut s'agir d'une méthode de projection d'opérateurs de construction précalculés sur une base réduite, ou de méthodes faisant appel à un domaine réduit. Les premiers prennent en entrée des opérateurs complets, les seconds des opérateurs réduits dans le but d'effectuer une deuxième opération de réduction.

        Question: expliquer pourquoi ce n'est pas équivalent à dire "opérations de la phase *offline* impliquant un domaine de calcul réduit"? Appeler ça "METHODE" plutôt qu'opérateur.

    CAS_REDUIT_A_RESOUDRE
        Ensemble des informations nécessaires à la réalisation de la phase *online*. On trouve donc des données du problème, les mêmes que celles qui ont servies à la définition du problème complet associé, mis à part que les données fixes ne sont que consultables, seules les données variables sont modifiables dans la plage spécifiée. On trouve également un solveur réduit assorti des opérateurs de constructions réduits qui le complètent.

        Question: quelle différence avec MODELE_REDUIT? Pour moi, c'est la même chose. Quest-ce qui pilote l'ensemble de la définition d'un CAS_REDUIT_A_RESOUDRE? Est-ce METHODE_DE_REDUCTION en délégant certaines parties à OPERATEUR_DE_COMPRESSION?

    HYPER_REDUCTION
        Méthode de compression définie par Ryckelynck et al [Ryckelyck09]_, consistant à résoudre un problème aux éléments finis sur un sous-maillage du maillage existant.

    POIDS
        Poids d'un schéma de quadrature utilisé pour approximer une intégrale.

    SUPPORT_INDEXATION
        Domaine de définition dans lequel les paramètres sont autorisés à prendre leurs valeurs *ou* ensemble mathématique discret permettant d'indexer de façon univoque des champs. Dans le premier cas, peut être défini par des bornes.

        Caractéristique: dans le cas des méthodes Greedy, on évalue un indicateur a posteriori sur un ensemble de points réparti sur le domaine paramétrique. On parle de *training set* dans la littérature. Dans ce cas, c'est l'attribut *échantillonage_previsionnel* qui porte cette information: c'est un candidat pour le réalisé.

    INDEXATION
        Valeur de paramètres pour laquelle une solution est effectivement disponible.

    VECTEUR_BASE_ORDRE_REDUIT
        *Champ* issu d'un algorithme de sélection (méthode base réduite) ou de compression (SVD) appliqué à une COLLECTION_SOLUTION_CAS.

    BASE_ORDRE_REDUIT
        Base de l'espace réduit sur lequel on projette les équations du problèmes. Collection de VECTEUR_BASE_ORDRE_REDUIT produite par une méthode de réduction et utilisée par une méthode de compression.

    BASE_REDUITE
        Désigne les méthodes de production d'une base d'ordre réduit reposant sur de sélections gloutonnes de vecteurs pour construire la base d'ordre réduit. Exemples: celles proposées par Maday, Prudhomme, Patera [Réfs?]

.. [Ryckelyck09] D. Ryckelynck, Hyper reduction of mechanical models involving internal variables, International Journal for Numerical Methods in Engineering, Volume 77, Issue 1, Pages: 75-89, (2009).
