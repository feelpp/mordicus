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

Utilisateur du modèle réduit boîte noire
========================================

Usage d'un modèle réduit pour réaliser un plan d'expérience
-----------------------------------------------------------

Exemple: utiliser un modèle réduit dans une boucle de calcul d'incertitude (CT)

    - **Objet :** effectuer des analyses (sensibilité, incertidus etc) nécessitant l'exécution d'un plan d'expérience qui serait trop coûteux avec le modèle complet
    - **Exigences :** rapidité du modèle réduit, fidélité du modèle réduit au modèle haute fidélité
    - **Notes :** même cas d'usage a priori que celui appelé par Phiméca "échantilloner le modèle réduit" et celui que CT a appelé "balayage paramétrique"

Utilisation d'un modèle réduit avec des mesures in-situ (en laboratoire, sur site de production...)
---------------------------------------------------------------------------------------------------

    - **Objet :** s'intégrer dans une démarche d'étude de systèmes physiques in-situ, avec des facilités pour l'usage boite noire du modèle réduit dans un environnement tourné vers l'expérimental ou la mesure, pas vers la simulation
    - **Exigences :** rapidité du modèle réduit, compatibilité des formats et intégration en environnements de mesures

Utilisation d'un modèle réduit comme brique d'un "clone digital" ou d'un code système
-------------------------------------------------------------------------------------

Exemple: utiliser un modèle réduit dans une modélisation système (MBSE, Modelica)

    - **Objet :** élaborer un modèle réduit, que l'on va utiliser en interaction en entrée et/ou en sortie avec des mesures
    - **Exigences :** un ou des indicateurs de fiabilité

Reconstruire un champ complet à partir des sorties d'un modèle réduit
---------------------------------------------------------------------

    - **Objet :** reconstruire un champ haute fidélité, ou simplement plus complet, à partir du modèle réduit
    - **Exigences :** un modèle réduit, un support du champ complet, un ou des indicateurs de fiabilité

Permettre la visualisation HPC des résultats du modèle réduit
-------------------------------------------------------------

    - **Objet :** les résultats de l'exploitation du modèle réduit représentent la physique haute fidélité, qui est évidemment d'un niveau de taille et de complexité similaire aux résultats du modèle haute fidélité que l'on a réduit. Cet exemple d'usage n'est donc d'intérêt que lorsque l'on ne peut pas établir à partir du modèle réduit le résultat haute fidélité comme intermédiaire d'entrée de la visualisation, pour cause de temps réel ou de taille informatique en particulier.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** visualisation temps réel ou de type Big Data

Archiver un modèle réduit ou une liste de modèles réduits
---------------------------------------------------------

    - **Objet :** lorsque l'on dispose d'un ou de plusieurs modèles réduits liés, pouvoir en garder une trace informatique que l'on pourra relire, comprendre et utiliser un certain temps plus tard. Cette fonction va au-delà de la simple sauvegarde qui permet seulement de conserver une trace immédiatement réutilisable du modèle réduit, mais n'assure pas sa pérennité ni sa relecture signifiante. Cela consiste aussi à permettre de retrouver un modèle réduit dans un grand nombre de modèles disponibles, d'effectuer un stockage suffisant dans être superflu, etc.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** une norme d'interprétation et un format de stockage avec une pérennité suffisante

Charger/ouvrir un modèle réduit archivé
---------------------------------------

En lien avec le use case précédent

.. todo::

   Yet to write

Sérialiser un modèle réduit pour le transmettre
-----------------------------------------------

En lien avec le use case précédent

.. todo::

   Yet to write

Gérer une taille mémoire prescrite pour l'élaboration d'un modèle réduit
------------------------------------------------------------------------

    - **Objet :** lors de l'élaboration d'un modèle réduit, on veut être capable de pouvoir satisfaire à une contrainte de taille mémoire (vive en premier lieu, et disque en second lieu) limitée de manière statique a priori ou dynamique en cours de calcul.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** des moyens de pilotage a priori ou en cours de calculs pour la réduction de modèles, des indicateurs de suivi des calculs

Garantir et contrôler qu'un modèle réduit conserve certaines propriétés mathématiques du modèle haute fidélité sur un sous-domaine
----------------------------------------------------------------------------------------------------------------------------------

    - **Objet :** dans ce cas, on désire que le modèle réduit présente le même comportement (par exemple convergence ou divergence de la représentation physique) sur le sous-domaine, et qu'on puisse le garantir
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un domaine d'équivalence de comportement

Couplage spatial entre un modèle réduit et un modèle haute fidélité
-------------------------------------------------------------------

    - **Objet :** en disposant d'un modèle haute fidélité sur un domaine complet, on veut utiliser le modèle réduit sur un sous-domaine spatial pour remplacer le modèle haute fidélité en le couplant. Ce cas peut être relié à l'exemple d'utilisation multi-échelles.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité, des moyens de couplage spatial entre le modèle réduit et le modèle haute fidélité
    - **Notes :** même cas d'usage que celui appelé par CT "couplage fort avec solveur autre"


Calculer des quantités physiques d'intérêt macroscopiques, par post-traitement (par ex durée de vie)
----------------------------------------------------------------------------------------------------

.. todo::

    Yet to write


Optimiser le placement des capteurs dans un système
---------------------------------------------------

.. todo::

    Yet to write

Evaluer le modèle réduit en un point (cas d'usage de plus bas niveau)
---------------------------------------------------------------------

.. todo::

    Yet to write

Utilisateur connaissant le modèle complet
=========================================

Création d'un modèle réduit avec garantie de fiabilité sur un domaine paramétrique donné
----------------------------------------------------------------------------------------

    - **Objet :** obtenir un modèle réduit, sans exigence de méthode particulière de réduction, mais avec un contrôle de sa fiabilité (erreur avec le modèle complet maintenue en dessous d'un certain seuil et contrôlable)
    - **Utilisateurs :** connaissant le modèle complet et/ou la physique représentée
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Comparer un modèle réduit romA avec un modèle haute-fidélité A
--------------------------------------------------------------

A rédiger si pas déjà le cas. Calcul d'un indicateur de fiabilité *a priori* pour évaluer la qualité de l'approximation

Comparer un modèle réduit romA avec un modèle haute fidélité B
--------------------------------------------------------------

    - **Objet :** comparer un modèle réduit 1, issu d'un modèle haute fidélité 1, avec un second modèle haute fidélité 2, potentiellement différent du modèle haute fidélité 1, mais représentant en théorie le même système physique
    - **Utilisateurs :** connaissant la physique représentée
    - **Exigences :** un modèle réduit 1, un modèle haute fidélité 2, un opérateur de distance entre des représentations physiques par modèles réduit ou haute fidélité

Comparer un modèle réduit romA avec des expériences (validation)
----------------------------------------------------------------

Objectif: valider la représentativité du modèle réduit

.. todo::

   Yet to write

Faire interagir un modèle réduit et des opérations de Data Science, typiquement pour obtenir un estimateur d'état
-----------------------------------------------------------------------------------------------------------------

    - **Objet :** si l'on dispose d'une représentation réduite d'un système physique, on veut l'utiliser pour effectuer des opérations que l'on nomme de manière générale de la Data Science (par exemple assimilation de données) : complément ou reprise d'apprentissage du modèle sur des mesures etc.
    - **Utilisateurs :** connaissant la physique représentée
    - **Exigences :** un ou des indicateurs de fiabilité, des opérateurs de comparaison, liens de contexte entre le modèle et les mesures

Utilisation in-situ pour accélérer la convergence du solveur non-linéaire HF
----------------------------------------------------------------------------

Exemple: modèle turbulent de Navier-Stokes (Sorbonne)

.. todo::

    Yet to write

Création d'un modèle réduit à pour un nouveau cas métier à partir d'un template existant de méthodologie de réduction
---------------------------------------------------------------------------------------------------------------------

.. todo::

    Yet to write

Utilisation d'un modèle réduit dans une boucle d'optimisation ou d'incertitude
------------------------------------------------------------------------------

Exemple: optimisation de loi de comportement sur une structure complexe

A déterminer: le modèle réduit est-il fixé au début de cette boucle ou peut-il évoluer à la volée en fonction de nouveaux calculs HF ?

.. todo::

    Yet to write

Calculer un indicateur de qualité a posterori pour un appel de modèle reduit
----------------------------------------------------------------------------

.. todo::

    A rédiger

Utilisateur sachant établir un modèle réduit
============================================


Création d'un modèle réduit en choisissant la méthode, pour un problème à variabilité paramétrique
--------------------------------------------------------------------------------------------------

    - **Objet :** élaborer un modèle réduit et/ou une base réduite, choisir dans les méthodes possibles de réduction, mettre à dispo de l'utilisateur boîte noire un modèle réduit expertisé
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Création d'un modèle réduit en choisissant la méthode, pour un problème à variabilité non paramétrique
------------------------------------------------------------------------------------------------------

.. todo::

   A rédiger


Création d'un modèle réduit en choisissant la méthode, pour un problème à variablité mixte paramétrique / non paramétrique
--------------------------------------------------------------------------------------------------------------------------

.. todo::

   A rédiger

Création d'un modèle réduit à partir de mesures ou de signaux I/O d'un modèle inconnu
-------------------------------------------------------------------------------------

    - **Objet :** élaborer un modèle réduit avec des informations venant de mesures, par exemple en utilisant une méthode intégrant des mesures (interpolation...), ou pour établir un surrogate du modèle haute fidélité à partir d'une famille de signaux d'entrée/sortie de ce modèle, etc.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Faire calculer une nouvelle simulation HF par le solveur "à la volée" pour une procédure de réduction qui le demande (bas niveau)
---------------------------------------------------------------------------------------------------------------------------------

.. todo::

   A rédiger

Modifier un modèle réduit pour (i) intégrer de nouvelles informations ou (ii) appliquer un niveau de réduction supplémentaire
-----------------------------------------------------------------------------------------------------------------------------

    - **Objet :** c'est principalement le cas dans des méthodes de réduction comme l'EIM incrémentale ou la POD suivie d'une EIM. Il y a un lien à faire avec l'exemple 3.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit 2, un ou des indicateurs de fiabilité

.. todo::

   A séparer en deux ?

Permettre le calcul multi-échelles ou multi-physiques de systèmes représentés par des modèles réduits
-----------------------------------------------------------------------------------------------------

    - **Objet :** la difficulté est de pouvoir représenter à l'aide de modèles réduits éventuellement en interaction une physique dont les caractéristiques multi-échelles ou multi-physiques doivent être préservées. Le préalable qui semble raisonnable est de disposer de cette même physique multi-\* représentée de manière satisfaisante à l'aide modèles haute fidélité avant de chercher à la représenter avec des modèles réduits.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** rapidité, liste de modèles réduits


Affichage ergonomique des informations contenues dans le modèle réduit (bases etc)
----------------------------------------------------------------------------------

    - **Objet :** la représentation d'un modèle réduit peut être notablement différente de ses résultats haute fidélité. Le but est donc de permettre sa compréhension et son interprétation en tant que tel, et non pas en tant que producteur de résultats haute fidélité.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, ergonomie de la représentation, capacité à servir pour une interprétation de modèle réduit

Construire un modèle réduit 3 en combinant deux modèles réduits 1 et 2 du même système
--------------------------------------------------------------------------------------

    - **Objet :** si l'on dispose déjà de deux modèles réduits de la même physique ou du même système, élaborer un troisième modèle réduit signifiant sans repasser dans l'espace de représentation des modèles haute fidélité
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Évaluer l'intérêt de la démarche "Offline+Modèle réduit" par rapport à l'utilisation directe du modèle haute fidélité
---------------------------------------------------------------------------------------------------------------------

    - **Objet :** comme l'élaboration d'un modèle réduit demande des ressources souvent conséquentes, il faut évaluer la rentabilité, en termes de ressources comme de temps, de l'élaboration d'un modèle réduit, et les bénéfices complémentaires que l'on peut attendre (comme une visualisation plus rapide ou simplement possible, une facilité pour des plans d'expérience, etc.)
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un ou des indicateurs pour évaluer les ressources nécessaires à établir un modèle réduit

Construire un modèle réduit lorsque le maillage (voire la géométrie) change entre les différents snapshots
----------------------------------------------------------------------------------------------------------

    - **Objet :** le changement de maillage à géométrie imposée est déjà fréquent dans les représentations de phénomènes non-linéaires comme des chocs, et les changements de géométrie peuvent être imposés par la physique étudiée (bulle en formation ou mouvement) ou par les buts de calcul (optimisation géométrique) par exemple
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité, des moyens de pilotage a priori ou en cours de calculs pour la réduction de modèles

Utilisation d'itérés de calcul comme snapshots pour effectuer la réduction
--------------------------------------------------------------------------

    - **Objet :** dans le cas d'un modèle haute fidélité qui nécessite des calculs intermédiaires (comme par exemple lors d'une convergence itérative), on désire pouvoir utiliser non seulement les résultats convergés, mais aussi les calculs intermédiaires pour établir la réduction du modèle.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Création d'un modèle réduit à partir d'un DoE déjà disponible (et sans possibilité de faire de nouveaux calculs HF)
-------------------------------------------------------------------------------------------------------------------

.. todo::

   A rédiger


Développer / brancher dans Mordicus une nouvelle méthodologie de réduction de modèles ou une variante d'une méthode existante
-----------------------------------------------------------------------------------------------------------------------------

.. todo::

   A rédiger

Générer une base réduite à partir d'un jeu de données de simulation (cas plus bas niveau)
-----------------------------------------------------------------------------------------

.. todo::

   A rédiger

Appeler une fonction utilisateur ou du code utilisateur lors de la phase online (bas niveau)
--------------------------------------------------------------------------------------------

.. todo::

   A rédiger

Construire une base réduite distribuée en mémoire (par DD) à partir de données de calcul distribuées en mémoire
---------------------------------------------------------------------------------------------------------------

.. todo::

   A rédiger

Tableau d'utilisation des cas d'usage par entité
================================================

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| USE CASE                              |  Participants                                                                            |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|                                       |  Score | Phi     | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisateur boîte noire                                                                                                          |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Usage d’un modèle réduit pour réaliser|   6    |   X     |  X    | X  |        |        |          |  X  |   X     |     |  X    |
| un plan d’expérience                  |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisation d’un modèle réduit avec   |        |         |       |    |        |        |          |     |         |     |       |
| des mesures in-situ (en laboratoire,  |   4    |         |  X    | X  |        |        |          |     |   X     |     |  X    |
| sur site de production...)            |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisation d'un modèle réduit comme  |        |         |       |    |        |        |          |     |         |     |       |
| brique d'un clone digital ou d'un     |   3    |         |       | X  |   X    |        |          |     |   X     |     |       |
| code système                          |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Reconstruire un champ complet à partir|        |         |       |    |        |        |          |     |         |     |       |
| des sorties d’un modèle réduit        |   4    |         |       |    |        |        |    X     |  X  |   X     |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Permettre la visualisation HPC des    |        |         |       |    |        |        |          |     |         |     |       |
| résultats du modèle réduit            |   5    |         |  X    | X  |        |        |    X     |     |   X     |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Archiver un modèle réduit             |   2    |         |       |    |   X    |        |          |     |   X     |     |       |
| ou une liste de modèles réduits       |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Charger/ouvrir un modèle réduit       |        |         |       |    |        |        |          |     |         |     |       |
| archivé                               |   3    |   X     |       |    |   X    |        |          | X   |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Sérialiser un modèle réduit           |   1    |   X     |       |    |        |        |          |     |         |     |       |
| pour le transmettre                   |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Gérer une taille mémoire prescrite    |   2    |         |       | X  |        |        |          |     |         |     |  X    |
| pour l’élaboration d’un modèle réduit |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Garantir et contrôler qu'un modèle    |        |         |       |    |        |        |          |     |         |     |       |
| réduit conserve certaines propriétés  |   3    |   X     |       |    |        |        |          | X   |   X     |     |       |
| mathématiques du modèle haute fidélité|        |         |       |    |        |        |          |     |         |     |       |
| sur un sous-domaine                   |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Couplage spatial entre un modèle      |        |         |       |    |        |        |          |     |         |     |       |
| réduit et un modèle haute fidélité    |   2    |         |       | X  |        |        |          |     |   X     |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Calculer des quantités d'intérêt      |        |         |       |    |        |        |          |     |         |     |       |
| physiques macro par post-traitement   |   2    |         |       | X  |        |        |          |     |         |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Optimiser le placement des capteurs   |        |         |       |    |        |        |          |     |         |     |       |
| dans un système                       |   1    |         |       |    |        |        |          |     |   X     |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Evaluer le modèle réduit en un point  |   ?    |         |       |    |        |        |          |     |         |     |       |
| (cas d'usage de plus bas niveau)      |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Calculer un indicateur de qualité     |   2    |         |       |    |        |        |          | X   |         |     |  X    |
| a posterori pour un appel de modèle   |        |         |       |    |        |        |          |     |         |     |       |
| reduit                                |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
.. raw:: latex

    \clearpage

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| USE CASE                              |  Participants                                                                            |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|                                       |  Score | Phi     | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisateur connaissant le modèle complet et/ou la physique                                                                      |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d'un modèle réduit avec      |        |         |       |    |        |        |          |     |         |     |       |
| garantie de fiabilité sur un          |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
| domaine paramétrique donné            |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Comparer un modèle réduit romA avec   |        |         |       |    |        |        |          |     |         |     |       |
| un modèle haute fidélité A            |   1    |         |       |    |        |        |    X     |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Comparer un modèle réduit romA avec   |        |         |       |    |        |        |          |     |         |     |       |
| un modèle haute fidélité B            |   5    |    X    |       | X  |        |        |    X     | X   |   X     |     |  x    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Comparer un modèle réduit romA avec   |        |         |       |    |        |        |          |     |         |     |       |
| des données expérimentales            |   1    |    X    |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Faire interagir un modèle réduit et   |        |         |       |    |        |        |          |     |         |     |       |
| des opérations de Data Science,       |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
| typiquement pour obtenir un estimateur|        |         |       |    |        |        |          |     |         |     |       |
| d'état                                |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisation d'un modèle réduit dans   |        |         |       |    |        |        |          |     |         |     |       |
| une boucle d'optimisation ou          |   6    |    X    |   X   | X  |        |        |          | X   |   X     |     |  X    |
| d'incertitudes                        |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d'un modèle réduit à pour un |        |         |       |    |        |        |          |     |         |     |       |
| nouveau cas métier à partir d'un      |   2    |         |       |    |        |        |          |     |         |     |       |
| template existant de méthodologie de  |        |         |       |    |        |   X    |    X     |     |         |     |       |
| réduction                             |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisation in-situ pour accélérer la |   2    |         |       |    |        |        |    X     | X   |         |     |       |
| convergence du solveur non-linéaire HF|        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+

.. raw:: latex

    \clearpage

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| USE CASE                              |  Participants                                                                            |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|                                       |  Score | Ph      | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisateur sachant établir le modèle réduit                                                                                     |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d'un modèle réduit en        |        |         |       |    |        |        |          |     |         |     |       |
| choisissant la méthode, pour un       |   7    |   X     |  X    | X  |   X    |        |    X     | X   |   X     |     |       |
| problème à variabilité paramétrique   |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d'un modèle réduit en        |        |         |       |    |        |        |          |     |         |     |       |
| choisissant la méthode, pour un       |   4    |         |       | X  |        |   X    |          |     |         |  X  |  X    |
| problème à variablité non paramétrique|        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d'un modèle réduit en        |        |         |       |    |        |        |          |     |         |     |       |
| choisissant la méthode, pour un       |   1    |         |       | X  |        |        |          |     |         |     |       |
| problème à variablité mixte           |        |         |       |    |        |        |          |     |         |     |       |
| paramétrique / non paramétrique       |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d’un modèle réduit à partir  |   4    |   X     |       | X  |        |        |          | X   |   X     |     |       |
| de mesures ou de signaux I/O d'un     |        |         |       |    |        |        |          |     |         |     |       |
| modèle inconnu                        |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Faire calculer une nouvelle simulation|        |         |       |    |        |        |          |     |         |     |       | 
| HF par le solveur "à la volée" pour   |        |         |       |    |        |        |          |     |         |     |       |
| une procédure de réduction qui le     |   3    |         |       | X  |        |        |    X     | X   |         |     |       |
| demande (bas niveau)                  |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Modifier un modèle réduit pour        |        |         |       |    |        |        |          |     |         |     |       | 
| (i) intégrer de nouvelles informations|        |         |       |    |        |        |          |     |         |     |       |
| ou                                    |   3    |         |       |    |        |   X    |          | X   |         |     |  X    |
| (ii) appliquer un niveau de réduction |        |         |       |    |        |        |          |     |         |     |       |
| supplémentaire                        |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Permettre le calcul multi-échelles ou |        |         |       |    |        |        |          |     |         |     |       |
| multi-physiques de systèmes           |   2    |         |       | X  |        |        |          |     |   X     |     |       |
| représentés par des modèles réduits   |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Affichage ergonomique des informations|        |         |       |    |        |        |          |     |         |     |       |
| contenues dans le modèle réduit       |   4    |         |       |    |        |   X    |    X     |     |   x     |     |  X    |
| (bases etc)                           |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Construire un modèle réduit 3 en      |        |         |       |    |        |        |          |     |         |     |       |
| combinant deux modèles réduits 1 et 2 |   3    |         |       | X  |        |   X    |          | X   |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Évaluer l’intérêt de la démarche      |        |         |       |    |        |        |          |     |         |     |       |
| “Offline+Modèle réduit” par rapport à |        |         |       |    |        |        |          |     |         |     |       |
| l’utilisation directe du modèle haute |   5    |   X     |       |    |        |   X    |    X     |     |   x     |     |  X    |
| fidélité                              |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Construire un modèle réduit lorsque   |        |         |       |    |        |        |          |     |         |     |       |
| le maillage (voire la géométrie)      |   2    |         |       | X  |        |        |    X     |     |         |     |       |
| change entre les différents snapshots |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisation d'itérés de calcul comme  |        |         |       |    |        |        |          |     |         |     |       |
| snapshots pour effectuer la réduction |   2    |         |       |    |        |   X    |          | X   |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d'un modèle réduit à partir  |        |         |       |    |        |        |          |     |         |     |       |
| d'un DoE déjà existant sans           |   1    |         |  X    |    |        |        |          |     |         |     |       |
| possibilité de faire de nouveaux      |        |         |       |    |        |        |          |     |         |     |       |
| calculs                               |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Développer / brancher dans Mordicus   |        |         |       |    |        |        |          |     |         |     |       |
| une nouvelle méthodologie de réduction|   1    |         |       |    |        |        |    X     |     |         |     |       |
| de modèles ou une variante            |        |         |       |    |        |        |          |     |         |     |       |
| d'une méthode existante               |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Générer une base réduite à partir d'un|   ?    |         |       |    |        |        |          |     |         |     |       |
| jeu de données de simulation (cas plus|        |         |       |    |        |        |          |     |         |     |       |
| bas niveau)                           |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Enrichir un plan d'expérience à partir|   1    |         |       | X  |        |        |          |     |         |     |       |
| d'un premier jeu de données de        |        |         |       |    |        |        |          |     |         |     |       |
| simulation                            |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Appeler une fonction utilisateur ou du|   2    |         |       |    |        |   X    |          | X   |         |     |       |
| code utilisateur lors de la phase     |        |         |       |    |        |        |          |     |         |     |       |
| online (bas niveau)                   |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Construire une base réduite distribuée|   2    |         |       |    |        |   X    |          | X   |         |     |       |
| en mémoire (par DD) à partir de       |        |         |       |    |        |        |          |     |         |     |       |
| données de calcul distribuées         |        |         |       |    |        |        |          |     |         |     |       |
| en mémoire                            |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+

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
