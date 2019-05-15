.. _glossary:

Glossaire
---------

A lire chronologiquement (idéalement).

.. glossary::

    CASE_TO_SOLVE
        Question d'intérêt à résoudre dans un domaine quelconque (*Larousse*), par un raisonnement scientifique traduisible en équations. On parle aussi de *problème*.

    SOLVING_PROCEDURE
        Ensemble d'opérations permettant la traduction en équations algébriques du problème à partir d'informations "de plus haut niveau" (*case data* et *solver options*), puis sa résolution. Il prend la forme d'un logiciel.

        :Question:

             Faut-il distinguer l'outil (le logiciel solveur) de la procédure de résolution ? Souhaité par CT, Soveur HF préciserait l'implémentation (logiciel, version) d'une méthode de résolution.

    SOLVEUR_OPTIONS => menage a faire (solver data? solver configuration ?)
        Pour un problème métier donné, représente les variantes disponibles dans le solveur pour le résoudre. On peut distinguer : (i) options de discrétisation en espace ou en temps, (ii) options de résolution algébriques (traitement des conditions de Dirichlet, solveur linéaire...), (iii) options d’exécution (version du code, serveur etc)
        Toutes les données nécessaires au solveur qui ne sont pas les paramètres par rapport auxquels on veut ou on pourrait vouloir réduire => pas vraiment donnees fixes, car on pourrait techniquement faire varier les données fixes.
        
        :Questions:

             Quelles différences avec *raw data* ?

             Le terme "options" entre en opposition oavec le contenu essentiel: maillage, type du solveur, version du code. Proposé: "solver configuration".

             Case data = données physique. Solver data = données numérique.


    SOLVEUR_HF OK
        Solveur développé et utilisé par les spécialistes du domaine considéré, préexistant à la tâche de réduction de modèles.

        Caractéristiques: Peut fonctionner sur des problèmes de grandes taille, à condition d'avoir des calculateurs appropriés. Difficile d'analyser les algorithmes mis en oeuvre autrement que par la documentation. Précis mais long. Code source volumineux et **peu ou pas modifiable**.

    DONNEES_DU_CAS (Case data) OK
        Informations "de haut niveau" définissant un cas à résoudre, utilisables par le solveur HF pour traduire le problème en équations, utilisable par le solveur HF pour traduire le problème en équations. C'est la description métier du problème à résoudre, le plus souvent, le "métier" consiste en l'étude d'un phénomène physique. On peut donc dire que la notion de *données du problème* représente l'ensemble de la description numérique de la physique du cas à résoudre. Les données sont la particularisation numérique des équations et de leurs paramètres. Par exemple, si loi de comportement = pb à résoudre; paramètres de la LdC = données du cas.

        :Questions: 

             Parle-t-on uniquement de la définition du problème continu ou également du problème discret?

             Autrement dit, regroupe-t-on sous ce vocabulaire toutes les données nécessaires à l'exécution d'un solveur HF?

             Faut-il distinguer entre (i) données de définition du problème **continu** (mise en données), (ii) options de discrétisation en espace ou en temps, (iii) options de résolution algébriques (traitement des conditions de Dirichlet, solveur linéaire...), (iv) options d'exécution (version du code, serveur etc).
 
        :Caractéristiques: 
        
             Ces données sont fournies au solveur sous une forme codifiée, le code dépendant du solveur.

             Certaines grandeurs ont une plage de variation plutôt qu'une valeur (DONNES_VARIABLES)

    DONNEES_FIXES OK
        Données réelles considérées pour la question d'intérêt comme invariantes. La valeur associée est fixe.

        :Remarques:

            TODO: Avec cette définition, pas de raison de faire le lien vers le maillage à cet endroit.

    DONNEES_VARIABLES
        Données considérées pour la question d'intérêt comme variables. On parle aussi de **paramètres**. Un cas possèdant des données variables est dit **paramétrique**. En termes d'attributs, une première information permet de savoir où elles s'insèrent dans la mise en donnée du problème **continu**: cela prend la forme d'un identifiant repris dans la mise en données du problème. D'autres informations peuvent décrire la nature physique de ce paramètre, en vue de les afficher dans le modèle réduit => DONNEES_IO.

        :Attributs:
            Une seconde information est le domaine de variation admissible => SUPPORT_INDEXATION

            TODO: Identifiant pour insertion dans la mise en données du problème.

            TODO: Informations sur la nature physique du paramètre.

            Optionnel: ensemble discret de valeurs à balayer, valeurs effectivement balayées.

        :Remarques:

            TODO: DONNEES_IO contiendrait DONNEES_VARIABLES

    DONNEES_INPUT_OUTPUT OK
        Description des entrées/sorties de la fonction de transfert, dont le réducteur de modèle non intrusif cherche une représentation réduite (plutôt adapté pour les méta-modèles).

    EDP
        Equation différentielle dont les solutions sont les fonctions inconnues dépendant de plusieurs variables vérifiant certaines conditions concernant leurs dérivées partielles

    SUPPORT_DISCRET OK
        Hiérarchie d’entités de :math:`\setR^N` (points, arêtes, faces, volumes...) sur lesquelles s’appuient à la fois la définition du problème et sa traduction en équations. Il doit prévoir la possibilité de tagguer des groupes d’entités. Des domaines de définition (espace, temps, paramètres ou une combinaison des précédents) peuvent être générés par produit cartésien de supports discrets.

        :Attribut:
            TODO: Eléments support par famille, selon leur nature géométrique (celle-ci étant précisée pour chaque famille).

        :Remarques:
            Le terme se rapport à la notion d'ensemble dénombrable, potentiellement peut prêter à confusion.

            TODO: changer le nom

            TODO: ajouter le lien avec l'espace d'approximation dont on a besoin pour passer de "state variable" à "champ".

    DOF_SUPPORT (support d'inconnue) OK
         Association entre (i) une entité géométrique ou un ensemble de plusieurs d’entités topologique et (ii) une ou plusieurs inconnues (1 ddl) du problème. Une inconnue a au plus un support. Dans la plupart des cas, ce sont des nœuds (éléments finis) ou des points (volumes finis), mais pas nécessairement.

        :Remarques:
            Attention: géométrie fait référence à la CAO. Pour faire référence à des entités d'un maillage, parler de toppologie.

    NUMBERING_SYSTEM (numérotation) OK
        Agrégation de supports de DDL de toutes les inconnues du problème. Sous forme de tableau d'entiers, reliant les numéros d'ordre (i) des supports et (ii) des inconnues.

    PHYSICAL QUANTITY (quantité physique ou grandeur) 
        Nature d’un résultat, elle est associée à une seule unité au sens (SI + sans unité).

        :Remarque:
            TODO: Faut-il préciser la nature locale ou globale (intensive ou extensive) de la grandeur.

            Comment seront gérée les unités différentes ?

    FIELD OK
        Valeurs portées par un support discret. Correspond à une seule quantité physique (éventuellement tensorielle). Peut être d’origine expérimentale ou un post-traitement, ou la sortie brute de la simulation dans les cas simples. Tous les points sur lesquels le champ porte une valeur (attention au cas données manquantes dans le cas d'une origine expérimentale) ont le même nombre de composantes. On peut évaluer un champ à n’importe quelle position à l’intérieur du domaine :math:`f(x)` à l'aide d'un APPROXIMATION_SPACE

       :Remarque:
           Attention au temporel comme support discret en particulier dans le cas où on change le maillage en temps => c'est l'objet COLLECTION_SOLUTION_CAS qui va alors gérer.

           TODO: FIELD à rapporter à SOLUTION_CAS ?

           TODO: Un field peut-il avoir un support en temps paramètres ? Traiter le cas de time series: classe dérivée ou classe sans rapport.

    UNKNOWN_VECTOR OK
           C’est le vecteur d’état (vecteur des variables d’état discrètes) X que le problème doit déterminer. C’est la sortie primale de la modélisation. Il peut mélanger des inconnues de différentes unités, autrement dit mélanger différentes quantités physiques : déplacement, pression, multiplicateur de Lagrange… Une inconnue peut être associée à un support de ddl. Ce n’est pas systématique (cf certains multiplicateur de Lagrange introduits de façon purement algébrique). Un vecteur d’inconnues est donc également associé à un support discret, mais de façon plus indirecte. Un vecteur d’inconnues agrège plusieurs vecteur d’état (multiplicateurs...), dont certaines peuvent ne pas avoir de représentation spatiale.

       :Remarque:
           TODO: Bien distinguer de la notion de variable d'état telle qu'introduite en physique.

    QUANTITY_VECTOR (state variable) OK
           Vecteur correspondant à une seule quantité physique et pouvant se représenter comme un champ via un espace d’approximation, lequel s’appuie sur le support discret. Exemples d’espaces d’approximation : espace polynomiaux par éléments associées aux éléments finis de Lagrange, de Hermite… A l’inverse, un champ se représente comme variable d’état par une méthode d’interpolation visant à définir un vecteur à partir d’opérations (éventuellement intégrales) sur les valeurs du champ.

       :Remarque:
           TODO: je parlerais de champ continu et de champ discret si c'est bien cette notion qui différencie FIELD et STATE_VARIABLE.

           TODO: Lien vers APPROXIMATION_SPACE à rajouter.

           A discuter: pas de lien avec le support discret directement.

    APPROXIMATION_SPACE

    MODELE OK
        Fonction du domaine de définition (paramètres x temps), qui donne en retourne une quantité d'intérêt pouvant être un champ. Tous les champs produits au final doivent se rapporter à un unique support discret « de référence » :math:`Omega_0`. La transformation avec d’éventuels supports discrets intermédiaires est masquée à l’intérieur de la fonction en quelque sorte.

        :Remarque:
             Un champ a été défini comme portant une unique quantité physique. La sortie peut être constituée de plusieurs champs.

             TODO: faire le lien avec DONNEES_INPUT_OUTPUT
   



    SUPPORT_SNAPSHOT
        Ensemble d'entités géométriques (points, arêtes, faces, volumes...) sur lesquelles s'appuient à la fois la définition du problème et sa traduction en équations. SUPPORT_SNAPSHOT est une généralisation de MAILLAGE qui permet d'inclure les méthodes à géométrie variable et d'autres use cases particulier (neutronique).

        Caractéristiques: Souvent de nature discrète (maillage) et de grande taille

        Exemples: points, arêtes, faces, volumes et ensemble les regroupant (maillage ou CAO)

        Questions: inclut-on également l'élément de référence et les fonctions de forme en EF? Parle-t-on du problème discret (maillage) ou continu (CAO)?

    MAILLAGE
        Spécialisation de SUPPORT_SNAPSHOT, c'est une discrétisation spaciale d'un milieu continu pouvant être directement utilisée par les méthodes numériques de résolution d'EDP communes: éléments finis ou volumes finis. Il s'agit d'un ensemble de cellules (ou encore éléments) dont l'intersection mutuelle est soit vide, soit une seul point, soit une arête, soit une face.

        Questions: les éléments qui constituent un maillage restent à définir plus précisément.

    SOLUTION_CAS ou SNAPSHOT OK

        Valeur d'une quantité solution pour laquelle le système d'équations **discret** est satisfait (*Larousse*), pour une valeur de (paramètre, temps) donnée. Une solution se rapporte, via son cas et éventuellement sa valeur de paramètre, à un SUPPORT_DISCRET. Une SOLUTION_CAS contient une **clé** (INDEXATION) permettant de repérer la valeur de (paramètre, temps) à laquelle elle se rapporte, et une **valeur** (attribut *field*) qui est un vecteur solution, par exemple un champ ou un vecteur d'inconnues

        Caractéristique: la *quantité mathématique* en question est souvent un *vecteur*. On parle souvent de *snapshot* en réduction de modèles.

        :Remarque:
            TODO: Expliciter la condition d'un unique support discret

            TODO: un snapshot peut-il directement être une quantité d'intérêt (une réalisation)

    COLLECTION_SOLUTIONS OK
        Ensemble de solutions, chacune étant qualifée par sa valeur des données variables (temps inclus), parmi les valeurs effectivement balayées.

        Caractéristique: souvent utilisée par les algorithme sous forme d'une matrice :math:`Q`, dite *matrice des snapshots*.

    INDEXING_SUPPORT OK
        Domaine de définition dans lequel les paramètres sont autorisés à prendre leurs valeurs *ou* ensemble mathématique discret permettant d'indexer de façon univoque des champs. Ce domaine de définition est défini par un produit de supports discrets.

        Caractéristique: dans le cas des méthodes Greedy, on évalue un indicateur a posteriori sur un ensemble de points réparti sur le domaine paramétrique. On parle de *training set* dans la littérature. Dans ce cas, c'est l'attribut *échantillonage_previsionnel* qui porte cette information: c'est un candidat pour le réalisé.

    INDEXING_VALUE OK
        Valeur de paramètres pour laquelle une solution est effectivement disponible.

    DOMAINE_REDUIT (Reduced domain)
        Filtre sur un SUPPORT_DISCRET, permettant de sélectionner des entités géométriques d'intérêt pour la construction d'opérateurs compressés. Exemple: points d’intégrations empiriques (nuage de points), éléments finis d’une hyper-réduction (sous-domaine de calcul réduit). Par filtre, on entend une sélection qui entraîne que le domaine réduit est un nouveau support discret.

       :Remarques:
            TODO: vérifier que le DOMAINE_REDUIT est une classe qui dérive de SUPPORT_DISCRET. Cette exigence est motivée car il doit pouvoir être indépendant des supports haute-fidélité.
        
        Caractéristique: souvent de petite taille.

        Exemple: points d'intégrations empiriques (NUAGE_DE_POINTS), éléments finis d'une hyper-réduction (SOUS_DOMAINE_DE_CALCUL_REDUIT)

    BUILDING_OPERATOR (OPERATEUR_DE_CONSTRUCTION) OK
        Toute donnée de nature non géométrique ou toute procédure utile à la traduction en équations **discrètes** du problème. Ce sont des "prises" ajustables complétant (le plus souvent) ou modifiant (plus rarement) l'ensemble d'opérations du solveur.

        Exemples: poids du schéma de quadrature, matrices et vecteurs précalculés, routine de comportement, fonctions de calcul des quantités duales, procédures de reconstruction du gradient, procédures d'assemblage particulières etc.

        Caractéristique: on peut imaginer qu'un certain nombre d'opérateurs de construction "classiques" soient présents dans l'implémentation par défaut. Certains opérateurs de constructions simples reposent sur des projections (produits matrices/vecteurs) à partir de matrices et vecteurs précalculées par un solveur HF. Ils doivent pouvoir être appelés depuis un calcul *complet* ou *réduit*.

        Questions: a priori, inclut également les routines permettant la traduction en équations du problème réduit à partir des coordonnées réduites? (Hypperreduction.ComputeReducedInternalForces et Hyperreduction.ComputeReducedGlobalTangentMatrix)? Faut-il distinguer donnée et procédure dans le modèle de données? Est-ce qu'on inclut les donnée ou procédure utile non pas à la traduction en équations, ms à la résolution algébrique? Classe dérivée "OPERATEUR_DE_PROJECTION"? Faire apparaître les matrices et vecteurs précalculés et l'entité informatique responsable de ce pré-calcul?

        :Remarque:
            Définition trop compliquée ou notion trop compliquée.

            TODO: a clarifier lors de la refonte des différents concepts.

    COMPRESSION_OF_DATA (METHODE_DE_REDUCTION) OK
        Opérations de la phase *offline* permettant la définition d'un petit nombre de fonctions de l'espace, dites "fonctions de bases", servant à la définition d'un espace réduit de recherche de la solution. Elle produit une base réduite, laquelle est tagguée (comment?) comme "base réduite".

        Question: expliquer pourquoi ce n'est pas équivalent à dire "opérations de la phase *offline* n'impliquant pas de domaine de calcul réduit"? Elle s'appuie sur la matrice des snapshots indépendamment du problème?

        :Remarques:
            TODO: vérifier que BASE_REDUITE dérive de COLLECTION_SOLUTIONS

    COMPRESSION_DES_OPERATEURS OK
        Opérations ayant pour but la production des opérateurs de construction d'un modèle réduit ou la diminution de leur complexité algorithmique (dans le but d'accélérer la phase *online*). Il produit des opérateurs de construction réduits. Exemples: il peut s’agir d’une méthode de projection d’opérateurs de construction précalculés sur une base réduite, ou de méthodes faisant appel à un domaine réduit. Les premiers prennent en entrée des opérateurs complets, les seconds des opérateurs réduits dans le but d’effectuer une deuxième opération de réduction.

        Caractéristique: il peut s'agir d'une méthode de projection d'opérateurs de construction précalculés sur une base réduite, ou de méthodes faisant appel à un domaine réduit. Les premiers prennent en entrée des opérateurs complets, les seconds des opérateurs réduits dans le but d'effectuer une deuxième opération de réduction.

        Question: expliquer pourquoi ce n'est pas équivalent à dire "opérations de la phase *offline* impliquant un domaine de calcul réduit"? Appeler ça "METHODE" plutôt qu'opérateur.

        :Remarques:
            TODO: changer l'intitulé dans le modèle de données.

    REDUCED_CASE_TO_SOLVE (CAS_REDUIT_A_RESOUDRE) OK
        Ensemble des informations nécessaires à la réalisation de la phase *online*. On trouve donc des données du problème, les mêmes que celles qui ont servies à la définition du problème complet associé, mis à part que les données fixes ne sont que consultables, seules les données variables sont modifiables dans la plage spécifiée. On trouve également un solveur réduit assorti des opérateurs de constructions réduits qui le complètent.

        Question: quelle différence avec MODELE_REDUIT? Pour moi, c'est la même chose. Quest-ce qui pilote l'ensemble de la définition d'un CAS_REDUIT_A_RESOUDRE? Est-ce METHODE_DE_REDUCTION en délégant certaines parties à OPERATEUR_DE_COMPRESSION?

    HYPER_REDUCTION OK
        Méthode de compression définie par Ryckelynck et al [Ryckelyck09]_, consistant à résoudre un problème aux éléments finis sur un sous-maillage du maillage existant.

    QUADRATURE_WEIGHTS (POIDS) OK
        Poids d'un schéma de quadrature utilisé pour approximer une intégrale.

        :Remarques:
            TODO: nom à changer dans le modèle de données

    VECTEUR_BASE_ORDRE_REDUIT OK
        *Champ* ou *vecteur d'inconnues* (suivant ce qui est nécessaire pour la méthode de compression a appliquer) issu d'un algorithme de sélection (méthode base réduite) ou de compression (SVD) appliqué à une COLLECTION_SOLUTIONS. Pour certaines applications, on parle de *mode* ou de *mode empirique*.

    BASE_ORDRE_REDUIT OK
        Base de l’espace réduit sur lequel on projette les équations du problème. Collection de vecteur de base d’ordre réduit produite par une COMPRESSION_DES_DONNEES et utilisée par une COMPRESSION_DES_OPERATEURS.

    RB_METHOD
        Désigne les méthodes de production d'une base d'ordre réduit reposant sur de sélections gloutonnes de vecteurs pour construire la base d'ordre réduit. Exemples: celles proposées par Maday, Prudhomme, Patera [Réfs?]

        :Remarques:
            TODO: changer le vocabulaire dans le modèle de données.

.. [Ryckelyck09] D. Ryckelynck, Hyper reduction of mechanical models involving internal variables, International Journal for Numerical Methods in Engineering, Volume 77, Issue 1, Pages: 75-89, (2009).
