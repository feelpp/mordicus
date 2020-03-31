.. note:: **Cas d'usage de la bibliothèque MOR_DICUS**

   *Contributeurs* : participants au Hackaton Mordicus du 21/11/2018

   *Auteur* : Jean-Philippe Argaud

   *Date*   : 21/11/2018


**Remarques générales**
-----------------------

Les cas sont synthétiquement décrits et sont uniquement classés par ordre
chronologique d'élaboration dans l'atelier. Les exigences décrivent
principalement ce qui est attendu en résultat du cas d'usage, en
indiquant aussi parfois ce qui est requis en même temps en entrée et en sortie
de l'exemple.

Ici, **les utilisateurs sont classés en 3 grandes catégories, incluses les unes
dans les autres** (la troisième catégorie contient la seconde, qui contient
elle-même la première, l'inverse n'étant pas vrai) :

#. Utilisateurs du modèle réduit en boite noire, sans le connaître (nommés "**Utilisateurs Boite Noire**")
#. Utilisateurs connaissant le modèle complet et/ou la physique représentée (nommés "**Utilisateurs connaissant le modèle complet et/ou la physique**")
#. Utilisateurs sachant élaborer le modèle réduit à partir du modèle complet (nommés "**Utilisateurs sachant établir un modèle réduit**")

Un certain nombre de cas d'usage décrits ci-dessous ont déjà été identifiés
comme étant à cheval entre des exemples potentiels d'utilisation et des sujets
de développement ou de recherche à part entière (donc hors exemples
d'utilisation). Cette distinction reste à discuter, ce qui pourrait conduire à
retirer certains exemples d'utilisation de la liste.

Les termes suivants sont à définir ou à nommer mathématiquement de manière
commune :

    - modèle réduit
    - modèle complet ou modèle haute fidélité
    - plan d'expérience
    - fiabilité (indicateur continu qualifiant l'erreur commise entre modèle haute fidélité et modèle réduit)
    - fidélité (satisfaction d'un critère quantitatif donné a priori sur la fiabilité)

A - Utilisateur du modèle réduit boîte noire
============================================

A.01 - Usage d'un modèle réduit pour réaliser un plan d'expérience
------------------------------------------------------------------

Exemple: utiliser un modèle réduit dans une boucle de calcul d'incertitude (CT)

    - **Objet :** effectuer des analyses (sensibilité, incertidus etc) nécessitant l'exécution d'un plan d'expérience qui serait trop coûteux avec le modèle complet
    - **Exigences :** rapidité du modèle réduit, fidélité du modèle réduit au modèle haute fidélité
    - **Notes :** même cas d'usage a priori que celui appelé par Phiméca "échantilloner le modèle réduit" et celui que CT a appelé "balayage paramétrique"

A.02 - Utilisation d'un modèle réduit avec des mesures in-situ (en laboratoire, sur site de production...)
----------------------------------------------------------------------------------------------------------

    - **Objet :** s'intégrer dans une démarche d'étude de systèmes physiques in-situ, avec des facilités pour l'usage boite noire du modèle réduit dans un environnement tourné vers l'expérimental ou la mesure, pas vers la simulation
    - **Exigences :** rapidité du modèle réduit, compatibilité des formats et intégration en environnements de mesures

A.03 - Utilisation d'un modèle réduit comme brique d'un "clone digital" ou d'un code système
--------------------------------------------------------------------------------------------

Exemple: utiliser un modèle réduit dans une modélisation système (MBSE, Modelica)

    - **Objet :** élaborer un modèle réduit, que l'on va utiliser en interaction en entrée et/ou en sortie avec des mesures
    - **Exigences :** un ou des indicateurs de fiabilité

A.04 - Reconstruire un champ complet à partir des sorties d'un modèle réduit
----------------------------------------------------------------------------

    - **Objet :** reconstruire un champ haute fidélité, ou simplement plus complet, à partir du modèle réduit
    - **Exigences :** un modèle réduit, un support du champ complet, un ou des indicateurs de fiabilité

A.05 - Permettre la visualisation HPC des résultats du modèle réduit
--------------------------------------------------------------------

    - **Objet :** les résultats de l'exploitation du modèle réduit représentent la physique haute fidélité, qui est évidemment d'un niveau de taille et de complexité similaire aux résultats du modèle haute fidélité que l'on a réduit. Cet exemple d'usage n'est donc d'intérêt que lorsque l'on ne peut pas établir à partir du modèle réduit le résultat haute fidélité comme intermédiaire d'entrée de la visualisation, pour cause de temps réel ou de taille informatique en particulier.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** visualisation temps réel ou de type Big Data

A.06 - Exporter (sérialiser) un modèle réduit au format d'échange
-----------------------------------------------------------------

    - **Objet:** écrire sur disque un modèle réduit à la fin de la phase *offline*, dans un format d'échange unique de la biblothèque Mordicus. Par "modèle réduit", on entend dans ce use case l'ensemble des opérateurs de complexité réduite et l'enchaînement d’opérations sur ces opérateurs qui permet d’approximer la réponse du modèle de façon plus rapide. Autrement dit, l'ensemble des données nécessaires pour réaliser le use case A.14 "évaluer le modèle réduit en un point".
    - **Exigence:** le modèle réduit ainsi sérialisé doit pouvoir être rechargé par la bibliothèque Mordicus plusieurs années après sa génération (compatibilité descendante). En effet, la phase online est réalisée par un utilisateur différent de la phase offline et potentiellement encore plusieurs années après que le modèle réduit ait été généré.
    - **A faire:** inventorier les autres cas d'usage qui auront besoin de celui-ci. On peut vouloir sérialiser le modèle réduit: (i) pour l'échanger entre partenaires, et dans ce cas un pickle suffit mais il faut tout de même que les deux partenaires puissent convertir leur modèle de données dans les mêmes classes en mémoire, (ii) pour l'archiver, (iii) pour faire un couplage de modèles etc.

A.07 - Importer (désérialiser) un modèle réduit au format d'échange
-------------------------------------------------------------------

    - **Objet:** importer en mémoire un modèle réduit qui a été écrit au format d'échange. 
    - **Exigence:** on doit pouvoir recharger un modèle réduit qui a été écrit avec une ancienne version de Mordicus.

A.08 - Archiver un modèle réduit ou une liste de modèles réduits
----------------------------------------------------------------

    - **Objet :** lorsque l'on dispose d'un ou de plusieurs modèles réduits liés, pouvoir en garder une trace informatique que l'on pourra relire, comprendre et utiliser un certain temps plus tard. Cette fonction va au-delà de la simple sauvegarde qui permet seulement de conserver une trace immédiatement réutilisable du modèle réduit, mais n'assure pas sa pérennité ni sa relecture signifiante. Cela consiste aussi à permettre de retrouver un modèle réduit dans un grand nombre de modèles disponibles, d'effectuer un stockage suffisant dans être superflu, etc.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** une norme d'interprétation et un format de stockage avec une pérennité suffisante

A.09 - Contrôler qu'un modèle réduit conserve certaines propriétés mathématiques du modèle haute fidélité sur un sous-domaine
-----------------------------------------------------------------------------------------------------------------------------------------

    - **Objet :** dans ce cas, on désire que le modèle réduit présente le même comportement (par exemple convergence ou divergence de la représentation physique) sur le sous-domaine, et qu'on puisse le garantir
    - **Exigences :** un domaine d'équivalence de comportement

A.10 - Couplage spatial entre un modèle réduit et un modèle haute fidélité
--------------------------------------------------------------------------

    - **Objet :** en disposant d'un modèle haute fidélité sur un domaine complet, on veut utiliser le modèle réduit sur un sous-domaine spatial pour remplacer le modèle haute fidélité en le couplant. Ce cas peut être relié à l'exemple d'utilisation multi-échelles.
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité, des moyens de couplage spatial entre le modèle réduit et le modèle haute fidélité
    - **Notes :** même cas d'usage que celui appelé par CT "couplage fort avec solveur autre"


A.11 - Calculer des quantités physiques d'intérêt macroscopiques, par post-traitement (par ex durée de vie)
-----------------------------------------------------------------------------------------------------------

    - **Objet:** on veut utiliser le modèle réduit pour calculer une grandeur d'intérêt pour l'ingénieur, souvent dérivée de l'intégrale d'un champ de sortie (par exemple débit, énergie, on valeur à un capteur modélisée par une intégrale sur un petit domaine). Il faut donc pouvoir post-traiter les résultats d'un modèle réduit pour pouvoir calculer une telle quantité.
    - **Notes:** on peut se permettre dans ce cas des méthodes où les champs (ou le vecteur d'état) ne sont pas précisément estimés, seule compte la précision sur la quantité d'intérêt.


A.12 - Optimiser le placement des capteurs dans un système
----------------------------------------------------------

    - **Objet:** étant donné une méthode d'estimation d'état d'un système (par exemple assimilation de données ou recalage), et un nombre de capteurs à positionner, on cherche le placement des capteurs qui permettra l'estimation avec la moins d'incertitude de l'état
    - **Notes:** il y a aussi une version incrémentale de ce cas d'usage: où placer le prochain capteur pour diminuer au plus l'incertitude sur l'estimation du champ.

A.13 - Evaluer le modèle réduit en un point (cas d'usage de plus bas niveau)
----------------------------------------------------------------------------

    - **Objet:** On souhaite évaluer le modèle réduit pour une nouvelle configuration (pour les cas paramétrique, pour une nouvelle valeur de paramètre). Ce cas d'usage est appelé par un certains nombre de cas de cet utilisateur.

A.14 - Calculer un indicateur de qualité a posteriori pour un appel de modèle reduit
------------------------------------------------------------------------------------

    - **Objet:** il s'agit de calculer un indicateur de qualité permettant de certifier l'approximation donnée par le modèle réduit. De tels indicateurs dépendent de la physique et de la nature du problème résolu, dont l'utilisateur connaissant la physique peut certifier qu'ils sont corrélée à l'erreur effective. Par exemple résidu d'équilibre en mécanique statique.
    - **Exigence:** le calcul de l'indicateur doit avoir une complexité inférieure ou égale à l'appel du modèle réduit lui-même

B - Utilisateur connaissant le modèle complet
=============================================

B.01 - Création d'un modèle réduit avec garantie de fiabilité sur un domaine paramétrique donné
-----------------------------------------------------------------------------------------------

    - **Objet :** obtenir un modèle réduit, sans exigence de méthode particulière de réduction, mais avec un contrôle de sa fiabilité (erreur avec le modèle complet maintenue en dessous d'un certain seuil et contrôlable).
    - **Note :** ce use case est typiquement mis en oeuvre à partir de scripts ou template de réduction (voir B.07) éventuellement pour différentes méthodes de réduction à mettre en conccurence, d'un indicateur de fiabilité et d'une méthode d'échantillonnage du modèle complet reposant sur cet indicateur de fiabilité. 
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

B.02 - Comparer un modèle réduit romA avec un modèle haute-fidélité A
---------------------------------------------------------------------

    - **Objet :** valider la qualité du modèle réduit en comparant la solution donnée par le modèle réduit et celle du modèle complet pour la même configuration (la même valeur de paramètre). La comparaison entre les deux solutions se fait selon une certaine norme (peut nécessiter la matrice d'un produit scalaire), et éventuellement uniquement sur un sous-domaine du domaine de calcul.

B.03 - Comparer un modèle réduit romA avec un modèle haute fidélité B
---------------------------------------------------------------------

    - **Objet :** comparer un modèle réduit 1, issu d'un modèle haute fidélité 1, avec un second modèle haute fidélité 2, potentiellement différent du modèle haute fidélité 1, mais représentant en théorie le même système physique
    - **Exigences :** un modèle réduit 1, un modèle haute fidélité 2, un opérateur de distance entre des représentations physiques par modèles réduit ou haute fidélité

B.04 - Comparer un modèle réduit romA avec des expériences (validation)
-----------------------------------------------------------------------

    - **Objet :** valider que le modèle réduit est représentatif du comportement d'un systèe physique donné, en comparant les résultat du modèle à des données expérimentales. Dans ce cas d'usage, on utilise le modèle réduit comme si c'était un modèle complet.
    - **Exigences :** pouvoir reconstruire les signaux numériques (souvent, à partir d'une intégrale sur les champs complets, lesquels sont eux même reconstruits à partir des champs réduits). On peut également disposer des stratégies pour obtenir directement les signaux numériques sans reconstruire les champs complets.
    - **Note :** souvent, les signaux sont obtenue comme un forme linéaire sur le champ complet (typiquement une intégrale sur un petit domaine pour un capteur en un point).

B.05 - Faire interagir un modèle réduit et des opérations de Data Science, typiquement pour obtenir un estimateur d'état
------------------------------------------------------------------------------------------------------------------------

    - **Objet :** si l'on dispose d'une représentation réduite d'un système physique, on veut l'utiliser pour effectuer des opérations que l'on nomme de manière générale de la Data Science (par exemple assimilation de données) : complément ou reprise d'apprentissage du modèle sur des mesures etc.
    - **Exigences :** un ou des indicateurs de fiabilité, des opérateurs de comparaison, liens de contexte entre le modèle et les mesures

B.06 - Utilisation in-situ pour accélérer la convergence du solveur non-linéaire HF
-----------------------------------------------------------------------------------

    - **Objet :** utiliser les solutions des pas de temps précédentes (voir même des itérations non convergées de la méthode de résolution) afin de stabiliser et accélérer la convergence de la méthode de résolution. 
    - **Exigences :** dans ce use case, les snapshots ne sont pas lus depuis un fichier disque, mais présent en mémoire vive durant le calcul haute-fidélité. Dans ce use case, le temps d'apprentissage (offline) compte: pour un pas de temps, il doit être inférieur au temps de résolution du pas de temps (sinon la méthode n'a pas d'intérêt). 
    - **Note :** l'utilisation de la réduction au cours de la résolution implique une solution au cas par cas pour chaque solveur. Ce use case concerne surtout la CFD, pour laquelle des outils précablés d'analyse in situ existent, utilisés pour faire de l'analyse et visualisation durant le calcul (par exemple Paraview catalyst). Si on vient se brancher sur un de ces outils, il faut qu'il permette le branchement des traitements que l'on souhaite. L'alternative est d'implémenter toute l'analyse dans le solveur (approche entièrement intrusive)

B.07 - Création d'un modèle réduit pour un nouveau cas métier à partir d'un template existant de méthodologie de réduction
--------------------------------------------------------------------------------------------------------------------------

    - **Objet :** pour un nouveau cas métier (une nouvelle étude) mais une physique et une nature de problème connue (par exemple Navier-Stokes laminaire), l'utilisateur B souhaite produire un modèle réduit à partir d'un template de réduction pour cette nature de problème qui lui a été fourni par l'utilisateur C.
    - **Exigence :** le template doit pouvoir être utilisé plusieurs années après sa création (car son créateur et son utilisateur sont deux utilisateurs différents qui potentiellement ne se connaissent pas).

B.08 - Utilisation d'un modèle réduit dans une boucle d'optimisation ou d'incertitude
-------------------------------------------------------------------------------------

    - **Objet :** le modèle réduit est utilisé dans une boucle d'optimisation (exemple calibrage de loi de comportement sur une structure complexe) ou de calcul d'incertitude, comme si c'était le modèle complet. L'objectif étant bien sûr un gain de temps et même de faisabilité (optimisations demandant un grand nombre d'évaluations qui ne seraient pas praticables avec un modèle complet).
    - **A déterminer :** le modèle réduit est-il fixé au début de cette boucle ou peut-il évoluer à la volée en fonction de nouveaux calculs HF ?

C - Utilisateur sachant établir un modèle réduit
================================================


C.01 - Création d'un modèle réduit en choisissant la méthode, pour un problème à variabilité paramétrique
---------------------------------------------------------------------------------------------------------

    - **Objet :** élaborer un modèle réduit et/ou une base réduite pour un problème à variabilité paramétrique (la configuration variable est décrite par quelques paramètres réels), choisir dans les méthodes possibles de réduction, mettre à dispo de l'utilisateur boîte noire un modèle réduit expertisé
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

C.02 - Création d'un modèle réduit en choisissant la méthode, pour un problème à variabilité non paramétrique
-------------------------------------------------------------------------------------------------------------

    - **Objet :** idem que C.01, mais pour un problème pour lequel la configuration variable ne peut pas être décrite par des paramètres réels. Il peut par exemple s'agir d'un cycle de chargement variable en entrée.
    - **Exigences :** pour toutes les méthodes de réduction, il faut néanmoins que les snapshots (les résultats de calcul complet desquels la méthode apprend) se rapportent tous au même maillage, ou que l'utilisateur fournisse un mapping qui permette de tous les rapporter au même maillage.


C.03 - Création d'un modèle réduit en choisissant la méthode, pour un problème à variablité mixte paramétrique / non paramétrique
---------------------------------------------------------------------------------------------------------------------------------

    - **Objet :** idem que C.01, avec une configuration variable ne pouvant que partiellement se ramener à des paramètres réels.

C.04 - Création d'un modèle réduit à partir de mesures ou de signaux I/O d'un modèle inconnu
--------------------------------------------------------------------------------------------

    - **Objet :** élaborer un modèle réduit avec des informations venant de mesures, par exemple en utilisant une méthode intégrant des mesures (interpolation...), ou pour établir un surrogate du modèle haute fidélité à partir d'une famille de signaux d'entrée/sortie de ce modèle, etc.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

C.05 - Faire calculer une nouvelle simulation HF par le solveur "à la volée" pour une procédure de réduction qui le demande (bas niveau)
----------------------------------------------------------------------------------------------------------------------------------------

    - **Objet :** ce use case n'est pas appelé par l'utilisateur directement mais par le système. Dans certaines méthodes - notamment dans le cadre de l'échantillonage du cas C.01 - la méthode de réduction doit savoir appeler le solveur haute-fidélité afin de calculer un nouveau snapshot. Autrement dit, les snapshots ne sont pas tous calculés au début de la méthode de réduction

C.06 - Modifier un modèle réduit pour (i) intégrer de nouvelles informations ou (ii) appliquer un niveau de réduction supplémentaire
------------------------------------------------------------------------------------------------------------------------------------

    - **Objet :** c'est principalement le cas dans des méthodes de réduction comme l'EIM incrémentale ou la POD suivie d'une EIM. Il y a un lien à faire avec l'exemple 3.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit 2, un ou des indicateurs de fiabilité

.. todo::

   A séparer en deux ?

C.07 - Permettre le calcul multi-échelles ou multi-physiques de systèmes représentés par des modèles réduits
------------------------------------------------------------------------------------------------------------

    - **Objet :** la difficulté est de pouvoir représenter à l'aide de modèles réduits éventuellement en interaction une physique dont les caractéristiques multi-échelles ou multi-physiques doivent être préservées. Le préalable qui semble raisonnable est de disposer de cette même physique multi-\* représentée de manière satisfaisante à l'aide modèles haute fidélité avant de chercher à la représenter avec des modèles réduits.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** rapidité, liste de modèles réduits


C.08 - Affichage ergonomique des informations contenues dans le modèle réduit (bases etc)
-----------------------------------------------------------------------------------------

    - **Objet :** la représentation d'un modèle réduit peut être notablement différente de ses résultats haute fidélité. Le but est donc de permettre sa compréhension et son interprétation en tant que tel, et non pas en tant que producteur de résultats haute fidélité.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, ergonomie de la représentation, capacité à servir pour une interprétation de modèle réduit

C.09 - Construire un modèle réduit 3 en combinant deux modèles réduits 1 et 2 du même système
---------------------------------------------------------------------------------------------

    - **Objet :** si l'on dispose déjà de deux modèles réduits de la même physique ou du même système, élaborer un troisième modèle réduit signifiant sans repasser dans l'espace de représentation des modèles haute fidélité
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

C.10 - Évaluer l'intérêt de la démarche "Offline+Modèle réduit" par rapport à l'utilisation directe du modèle haute fidélité
----------------------------------------------------------------------------------------------------------------------------

    - **Objet :** comme l'élaboration d'un modèle réduit demande des ressources souvent conséquentes, il faut évaluer la rentabilité, en termes de ressources comme de temps, de l'élaboration d'un modèle réduit, et les bénéfices complémentaires que l'on peut attendre (comme une visualisation plus rapide ou simplement possible, une facilité pour des plans d'expérience, etc.)
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un ou des indicateurs pour évaluer les ressources nécessaires à établir un modèle réduit

C.11 - Construire un modèle réduit lorsque le maillage (voire la géométrie) change entre les différents snapshots
-----------------------------------------------------------------------------------------------------------------

    - **Objet :** le changement de maillage à géométrie imposée est déjà fréquent dans les représentations de phénomènes non-linéaires comme des chocs, et les changements de géométrie peuvent être imposés par la physique étudiée (bulle en formation ou mouvement) ou par les buts de calcul (optimisation géométrique) par exemple
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité, des moyens de pilotage a priori ou en cours de calculs pour la réduction de modèles

C.12 - Utilisation d'itérés de calcul comme snapshots pour effectuer la réduction
---------------------------------------------------------------------------------

    - **Objet :** dans le cas d'un modèle haute fidélité qui nécessite des calculs intermédiaires (comme par exemple lors d'une convergence itérative), on désire pouvoir utiliser non seulement les résultats convergés, mais aussi les calculs intermédiaires pour établir la réduction du modèle.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

C.13 - Création d'un modèle réduit à partir d'un DoE déjà disponible (et sans possibilité de faire de nouveaux calculs HF)
--------------------------------------------------------------------------------------------------------------------------

    - **Objet :** création du "meilleur modèle réduit possible", à partir de résultats de calcul déjà disponibles, mais achetés ou effectués par un autre utilisateur - et même éventuellement avec un code dont on ne dispose pas - et donc sans possibilité de faires de nouveaux calculs.
    - **Note :** éventuellement, si un indicateur a posteriori existe, on pourra évaluer le domaine paramétrique sur lequel le modèle réduit produit est valable (au sens d'une certaine tolérance).

C.14 - Développer / brancher dans Mordicus une nouvelle méthodologie de réduction de modèles ou une variante d'une méthode existante
------------------------------------------------------------------------------------------------------------------------------------

    - **Objet :** il s'agit, pour un ingénieur chercheur développeur de méthodes mais pas nécessairement au fait de toute l'architecture de Mordicus, de pouvoir insérer dans Mordicus une nouvelle méthode de réduction.
    - **Exigence :** l'utilisateur doit avoir un tutoriel et/ou un exemple bac à sable pour démarrer.
    - **Utilisateur :** sachant établir un modèle réduit ET développeur de Mordicus.

C.15 - Générer une base réduite à partir d'un jeu de données de simulation (cas plus bas niveau)
------------------------------------------------------------------------------------------------

    - **Objet :** ce cas d'usage est rarement un but en soi, mais un sous-cas d'un très grand nombre de cas d'usage. Il s'agit de construire une base avec un nombre réduit de fonction permettant d'approcher la variété des solutions complètes. Il s'agit d'une étape intermédiaire dans un très grand nombre de méthodes.
    - **Note :** c'est l'étape dite de compression des données. Peut se faire par POD, par POD incrémentale, par des méthodes de sélection gloutonne / réorthogonalisation...

C.16 - Appeler une fonction utilisateur ou du code utilisateur lors de la phase online (bas niveau)
---------------------------------------------------------------------------------------------------

    - **Objet :** l'enchaînement des opérations qui constitue l'évaluation du modèle réduit peut être complexe, et, pour ne pas avoir à être recodée, appeler le même code qui a servi à générer les snapshot (méthode dite intrusive) ou appeler des fonctions utilisateurs (par exemple une loi de comportement).
    - **Exigence :** il faut pouvoir formaliser ces appels à la sérialisation (use case A.06)

C.17 - Construire une base réduite distribuée en mémoire (par DD) à partir de données de calcul distribuées en mémoire
----------------------------------------------------------------------------------------------------------------------

    - **Objet :** même but que C.15, mais les snapshots sont trop volumineux pour être stockés sur un seul noeud de calcul et sont distribués sur plusieurs noeuds, chaque noeud contenant la restriction des résultats à un sous-domaine. Il en sera donc de même des éléments de la base réduite, qui ont la même taille que les résultats de calcul. L'enjeu est donc de pouvoir effectuer la compression des données de façon parallèle, par sous-domaine, dans jamais ramener l'ensemble du champ à un seul noeud.

C.18 - Garantir qu'un modèle réduit conserve certaines propriétés mathématiques du modèle haute fidélité sur un sous-domaine
----------------------------------------------------------------------------------------------------------------------------

    - **Objet :** dans ce cas, on désire que le modèle réduit présente le même comportement (par exemple convergence ou divergence de la représentation physique) sur le sous-domaine, et qu'on puisse le garantir
    - **Exigences :** un domaine d'équivalence de comportement

C.19 - Gérer une taille mémoire prescrite pour l'élaboration d'un modèle réduit
-------------------------------------------------------------------------------

    - **Objet :** lors de l'élaboration d'un modèle réduit, on veut être capable de pouvoir satisfaire à une contrainte de taille mémoire (vive en premier lieu, et disque en second lieu) limitée de manière statique a priori ou dynamique en cours de calcul.
    - **Exigences :** des moyens de pilotage a priori ou en cours de calculs pour la réduction de modèles, des indicateurs de suivi des calculs

Tableau d'utilisation des cas d'usage par entité
================================================

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|    | USE CASE                              |  Participants                                                                            |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|    |                                       |  Score | Phi     | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| A  | Utilisateur boîte noire                                                                                                          |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.01| Usage d’un modèle réduit pour réaliser|   6    |   X     |  X    | X  |        |        |          |  X  |   X     |     |  X    |
|    | un plan d’expérience                  |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.02| Utilisation d’un modèle réduit avec   |        |         |       |    |        |        |          |     |         |     |       |
|    | des mesures in-situ (en laboratoire,  |   4    |         |  X    | X  |        |        |          |     |   X     |     |  X    |
|    | sur site de production...)            |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.03| Utilisation d'un modèle réduit comme  |        |         |       |    |        |        |          |     |         |     |       |
|    | brique d'un clone digital ou d'un     |   3    |         |       | X  |   X    |        |          |     |   X     |     |       |
|    | code système                          |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.04| Reconstruire un champ complet à partir|        |         |       |    |        |        |          |     |         |     |       |
|    | des sorties d’un modèle réduit        |   4    |         |       |    |        |        |    X     |  X  |   X     |     |  X    |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.05| Permettre la visualisation HPC des    |        |         |       |    |        |        |          |     |         |     |       |
|    | résultats du modèle réduit            |   5    |         |  X    | X  |        |        |    X     |     |   X     |     |  X    |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.06| Exporter (sérialiser) un modèle réduit|        |         |       |    |        |        |          |     |         |     |       |
|    | au format d'échange                   |   3    |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.07| Importer (désérialiser) un modèle     |        |         |       |    |        |        |          |     |         |     |       |
|    | réduit au format d'échange            |   3    |   X     |       |    |   X    |        |          |     |   X     |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.08| Archiver un modèle réduit             |   2    |         |       |    |   X    |        |          |     |   X     |     |       |
|    | ou une liste de modèles réduits       |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.09| Contrôler qu'un modèle                |        |         |       |    |        |        |          |     |         |     |       |
|    | réduit conserve certaines propriétés  |   3    |   X     |       |    |        |        |          | X   |   X     |     |       |
|    | mathématiques du modèle haute fidélité|        |         |       |    |        |        |          |     |         |     |       |
|    | sur un sous-domaine                   |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.10| Couplage spatial entre un modèle      |        |         |       |    |        |        |          |     |         |     |       |
|    | réduit et un modèle haute fidélité    |   2    |         |       | X  |        |        |          |     |   X     |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.11| Calculer des quantités d'intérêt      |        |         |       |    |        |        |          |     |         |     |       |
|    | physiques macro par post-traitement   |   2    |         |       | X  |        |        |          |     |         |     |  X    |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.12| Optimiser le placement des capteurs   |        |         |       |    |        |        |          |     |         |     |       |
|    | dans un système                       |   1    |         |       |    |        |        |          |     |   X     |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.13| Evaluer le modèle réduit en un point  |   ?    |         |       |    |        |        |          |     |         |     |       |
|    | (cas d'usage de plus bas niveau)      |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|A.14| Calculer un indicateur de qualité     |   2    |         |       |    |        |        |          | X   |         |     |  X    |
|    | a posteriori pour un appel de modèle  |        |         |       |    |        |        |          |     |         |     |       |
|    | reduit                                |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+

.. raw:: latex

    \clearpage

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|    | USE CASE                              |  Participants                                                                            |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|    |                                       |  Score | Phi     | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| B  | Utilisateur connaissant le modèle complet et/ou la physique                                                                      |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.01| Création d'un modèle réduit avec      |        |         |       |    |        |        |          |     |         |     |       |
|    | garantie de fiabilité sur un          |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
|    | domaine paramétrique donné            |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.02| Comparer un modèle réduit romA avec   |        |         |       |    |        |        |          |     |         |     |       |
|    | un modèle haute fidélité A            |   1    |         |       |    |        |        |    X     |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.03| Comparer un modèle réduit romA avec   |        |         |       |    |        |        |          |     |         |     |       |
|    | un modèle haute fidélité B            |   5    |    X    |       | X  |        |        |    X     | X   |   X     |     |  x    |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.04| Comparer un modèle réduit romA avec   |        |         |       |    |        |        |          |     |         |     |       |
|    | des données expérimentales            |   1    |    X    |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.05| Faire interagir un modèle réduit et   |        |         |       |    |        |        |          |     |         |     |       |
|    | des opérations de Data Science,       |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
|    | typiquement pour obtenir un estimateur|        |         |       |    |        |        |          |     |         |     |       |
|    | d'état                                |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.06| Utilisation d'un modèle réduit dans   |        |         |       |    |        |        |          |     |         |     |       |
|    | une boucle d'optimisation ou          |   6    |    X    |   X   | X  |        |        |          | X   |   X     |     |  X    |
|    | d'incertitudes                        |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.07| Création d'un modèle réduit à pour un |        |         |       |    |        |        |          |     |         |     |       |
|    | nouveau cas métier à partir d'un      |   2    |         |       |    |        |        |          |     |         |     |       |
|    | template existant de méthodologie de  |        |         |       |    |        |   X    |    X     |     |         |     |       |
|    | réduction                             |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|B.08| Utilisation in-situ pour accélérer la |   2    |         |       |    |        |        |    X     | X   |         |     |       |
|    | convergence du solveur non-linéaire HF|        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+

.. raw:: latex

    \clearpage

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|    | USE CASE                              |  Participants                                                                            |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|    |                                       |  Score | Ph      | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| C  | Utilisateur sachant établir le modèle réduit                                                                                     |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.01| Création d'un modèle réduit en        |        |         |       |    |        |        |          |     |         |     |       |
|    | choisissant la méthode, pour un       |   7    |   X     |  X    | X  |   X    |        |    X     | X   |   X     |     |       |
|    | problème à variabilité paramétrique   |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.02| Création d'un modèle réduit en        |        |         |       |    |        |        |          |     |         |     |       |
|    | choisissant la méthode, pour un       |   4    |         |       | X  |        |   X    |          |     |         |  X  |  X    |
|    | problème à variablité non paramétrique|        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.03| Création d'un modèle réduit en        |        |         |       |    |        |        |          |     |         |     |       |
|    | choisissant la méthode, pour un       |   1    |         |       | X  |        |        |          |     |         |     |       |
|    | problème à variablité mixte           |        |         |       |    |        |        |          |     |         |     |       |
|    | paramétrique / non paramétrique       |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.04| Création d’un modèle réduit à partir  |   4    |   X     |       | X  |        |        |          | X   |   X     |     |       |
|    | de mesures ou de signaux I/O d'un     |        |         |       |    |        |        |          |     |         |     |       |
|    | modèle inconnu                        |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.05| Faire calculer une nouvelle simulation|        |         |       |    |        |        |          |     |         |     |       | 
|    | HF par le solveur "à la volée" pour   |        |         |       |    |        |        |          |     |         |     |       |
|    | une procédure de réduction qui le     |   3    |         |       | X  |        |        |    X     | X   |         |     |       |
|    | demande (bas niveau)                  |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.06| Modifier un modèle réduit pour        |        |         |       |    |        |        |          |     |         |     |       | 
|    | (i) intégrer de nouvelles informations|        |         |       |    |        |        |          |     |         |     |       |
|    | ou                                    |   3    |         |       |    |        |   X    |          | X   |         |     |  X    |
|    | (ii) appliquer un niveau de réduction |        |         |       |    |        |        |          |     |         |     |       |
|    | supplémentaire                        |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.07| Permettre le calcul multi-échelles ou |        |         |       |    |        |        |          |     |         |     |       |
|    | multi-physiques de systèmes           |   2    |         |       | X  |        |        |          |     |   X     |     |       |
|    | représentés par des modèles réduits   |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.08| Affichage ergonomique des informations|        |         |       |    |        |        |          |     |         |     |       |
|    | contenues dans le modèle réduit       |   4    |         |       |    |        |   X    |    X     |     |   x     |     |  X    |
|    | (bases etc)                           |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.09| Construire un modèle réduit 3 en      |        |         |       |    |        |        |          |     |         |     |       |
|    | combinant deux modèles réduits 1 et 2 |   3    |         |       | X  |        |   X    |          | X   |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.10| Évaluer l’intérêt de la démarche      |        |         |       |    |        |        |          |     |         |     |       |
|    | “Offline+Modèle réduit” par rapport à |        |         |       |    |        |        |          |     |         |     |       |
|    | l’utilisation directe du modèle haute |   5    |   X     |       |    |        |   X    |    X     |     |   x     |     |  X    |
|    | fidélité                              |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.11| Construire un modèle réduit lorsque   |        |         |       |    |        |        |          |     |         |     |       |
|    | le maillage (voire la géométrie)      |   2    |         |       | X  |        |        |    X     |     |         |     |       |
|    | change entre les différents snapshots |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.12| Utilisation d'itérés de calcul comme  |        |         |       |    |        |        |          |     |         |     |       |
|    | snapshots pour effectuer la réduction |   2    |         |       |    |        |   X    |          | X   |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.13| Création d'un modèle réduit à partir  |        |         |       |    |        |        |          |     |         |     |       |
|    | d'un DoE déjà existant sans           |   1    |         |  X    |    |        |        |          |     |         |     |       |
|    | possibilité de faire de nouveaux      |        |         |       |    |        |        |          |     |         |     |       |
|    | calculs                               |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.14| Développer / brancher dans Mordicus   |        |         |       |    |        |        |          |     |         |     |       |
|    | une nouvelle méthodologie de réduction|   1    |         |       |    |        |        |    X     |     |         |     |       |
|    | de modèles ou une variante            |        |         |       |    |        |        |          |     |         |     |       |
|    | d'une méthode existante               |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.15| Générer une base réduite à partir d'un|   ?    |         |       |    |        |        |          |     |         |     |       |
|    | jeu de données de simulation (cas plus|        |         |       |    |        |        |          |     |         |     |       |
|    | bas niveau)                           |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.17| Enrichir un plan d'expérience à partir|   1    |         |       | X  |        |        |          |     |         |     |       |
|    | d'un premier jeu de données de        |        |         |       |    |        |        |          |     |         |     |       |
|    | simulation                            |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.18| Appeler une fonction utilisateur ou du|   2    |         |       |    |        |   X    |          | X   |         |     |       |
|    | code utilisateur lors de la phase     |        |         |       |    |        |        |          |     |         |     |       |
|    | online (bas niveau)                   |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.19| Construire une base réduite distribuée|   2    |         |       |    |        |   X    |          | X   |         |     |       |
|    | en mémoire (par DD) à partir de       |        |         |       |    |        |        |          |     |         |     |       |
|    | données de calcul distribuées         |        |         |       |    |        |        |          |     |         |     |       |
|    | en mémoire                            |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.20| Garantir qu'un modèle                 |        |         |       |    |        |        |          |     |         |     |       |
|    | réduit conserve certaines propriétés  |   3    |   X     |       |    |        |        |          | X   |   X     |     |       |
|    | mathématiques du modèle haute fidélité|        |         |       |    |        |        |          |     |         |     |       |
|    | sur un sous-domaine                   |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|C.21| Gérer une taille mémoire prescrite    |   2    |         |       | X  |        |        |          |     |         |     |  X    |
|    | pour l’élaboration d’un modèle réduit |        |         |       |    |        |        |          |     |         |     |       |
+----+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+

Exigences supplémentaires potentielles
--------------------------------------

Les exigences suivantes sont apparues dans les questionnaires.

Exigence pour certaines méthodes: communiquer directement avec les codes de simulation par API (exemple NIRB).

Pour l'utilisateur boîte noire:

    * pouvoir utiliser un ordinateur de bureau plutôt qu'un cluster

Pour l'utilisateur connaissant le modèle complet et/ou la physique:

    * calcul des champs mécaniques pour un grand nombre de cycles de chargement;

    * pouvoir faire un post-processing complexe

    * le modèle réduit doit alléger le temps de calcul en conservant au mieux les propriétés non-linéaires

    * Mordicus doit supporter les structures de données distribuées (HPC)

Pour l'utilisateur sachant construire un modèle réduit:

    * pouvoir changer rapidement les options de constructions du modèle réduit (exigence ou cas d'usage ?);

    * que le système suggère des alternatives / autres méthodes;

    * la réduction d'un modèle doit être facile et procurer un estimateur d'erreur;

    * l'archivage d'un modèle réduit doit être autonome et documenté.

Que faire avec tous ces cas d'usage? Faut-il les détailler?

Non: objet/ exigences/ données ou composants concernés (après avoir fait le modèle de données)

Voir s'il y en a d'autres à la lumière des exemples d'utilisation
