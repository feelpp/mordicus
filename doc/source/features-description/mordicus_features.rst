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

Usage d'un modèle réduit en plan d'expérience
---------------------------------------------

    - **Objet :** effectuer des analyses en plans d'expériences
    - **Utilisateurs :** Boite Noire
    - **Exigences :** rapidité du modèle réduit, fidélité du modèle réduit au modèle haute fidélité
    - **Notes :** même cas d'usage a priori que celui appelé par Phiméca "échantilloner le modèle réduit" et celui que CT a appelé "balayage paramétrique"

Création d'un modèle réduit pour effectuer un plan d'expérience
---------------------------------------------------------------

    - **Objet :** obtenir un modèle réduit, sans exigence de méthode particulière de réduction, mais avec un contrôle de sa fiabilité
    - **Utilisateurs :** connaissant le modèle complet et/ou la physique représentée
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Création d'un modèle réduit
---------------------------

    - **Objet :** élaborer un modèle réduit et/ou une base réduite, choisir dans les méthodes possibles de réduction, disposer d'un modèle réduit expertisé
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Utilisation d'un modèle réduit avec des mesures in-situ (en laboratoire, sur site de production...)
---------------------------------------------------------------------------------------------------

    - **Objet :** s'intégrer dans une démarche d'étude de systèmes physiques in-situ, avec des facilités pour l'usage boite noire du modèle réduit dans un environnement tourné vers l'expérimental ou la mesure, pas vers la simulation
    - **Utilisateurs :** Boite Noire
    - **Exigences :** rapidité du modèle réduit, compatibilité des formats et intégration en environnements de mesures

Création d'un modèle réduit avec des mesures
--------------------------------------------

    - **Objet :** élaborer un modèle réduit avec des informations venant de mesures, par exemple en utilisant une méthode intégrant des mesures (interpolation...), ou pour établir les simulations du modèle haute fidélité, etc.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Disposer d'un "clone digital" basé sur un modèle réduit
-------------------------------------------------------

    - **Objet :** élaborer un modèle réduit, que l'on va utiliser en interaction en entrée et/ou en sortie avec des mesures
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un ou des indicateurs de fiabilité

Générer un champ complet à partir d'un modèle réduit
----------------------------------------------------

    - **Objet :** reconstruire un champ haute fidélité, ou simplement plus complet, à partir du modèle réduit
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un modèle réduit, un support du champ complet, un ou des indicateurs de fiabilité

Déduire un modèle réduit 2 à partir d'un modèle réduit 1
--------------------------------------------------------

    - **Objet :** c'est principalement le cas dans des méthodes de réduction comme l'EIM incrémentale ou la POD suivie d'une EIM. Il y a un lien à faire avec l'exemple 3.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit 2, un ou des indicateurs de fiabilité

Comparer un modèle réduit 1 avec un modèle haute fidélité 2
-----------------------------------------------------------

    - **Objet :** comparer un modèle réduit 1, issu d'un modèle haute fidélité 1, avec un second modèle haute fidélité 2, potentiellement différent du modèle haute fidélité 1, mais représentant en théorie le même système physique
    - **Utilisateurs :** connaissant la physique représentée
    - **Exigences :** un modèle réduit 1, un modèle haute fidélité 2, un opérateur de distance entre des représentations physiques par modèles réduit ou haute fidélité

Optimisation de loi(s) de comportement sur structure complexe
-------------------------------------------------------------

    - **Objet :** le but est de pouvoir disposer d'un modèle réduit qui permette de représenter fidèlement la physique à optimiser sur un milieu hétérogène, comme dans un matériau cristallin pour lequel les propriétés du matériau changent entre chaque grain, et le volume observé contient un grand nombre de grains (10 puissance...)
    - **Utilisateurs :** connaissant la physique représentée
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Permettre le calcul multi-échelles ou multi-physiques de systèmes représentés par des modèles réduits
-----------------------------------------------------------------------------------------------------

    - **Objet :** la difficulté est de pouvoir représenter à l'aide de modèles réduits éventuellement en interaction une physique dont les caractéristiques multi-échelles ou multi-physiques doivent être préservées. Le préalable qui semble raisonnable est de disposer de cette même physique multi-\* représentée de manière satisfaisante à l'aide modèles haute fidélité avant de chercher à la représenter avec des modèles réduits.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** rapidité, liste de modèles réduits

Permettre la visualisation des résultats du modèle réduit
---------------------------------------------------------

    - **Objet :** les résultats de l'exploitation du modèle réduit représentent la physique haute fidélité, qui est évidemment d'un niveau de taille et de complexité similaire aux résultats du modèle haute fidélité que l'on a réduit. Cet exemple d'usage n'est donc d'intérêt que lorsque l'on ne peut pas établir à partir du modèle réduit le résultat haute fidélité comme intermédiaire d'entrée de la visualisation, pour cause de temps réel ou de taille informatique en particulier.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** visualisation temps réel ou de type Big Data

Permettre la visualisation du modèle réduit lui-même
----------------------------------------------------

    - **Objet :** la représentation d'un modèle réduit peut être notablement différente de ses résultats haute fidélité. Le but est donc de permettre sa compréhension et son interprétation en tant que tel, et non pas en tant que producteur de résultats haute fidélité.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, ergonomie de la représentation, capacité à servir pour une interprétation de modèle réduit

Faire interagir un modèle réduit et des opérations de Data Science
------------------------------------------------------------------

    - **Objet :** si l'on dispose d'une représentation réduite d'un système physique, on veut l'utiliser pour établir des opérations que l'on nomme de manière générale de la Data Science : complément ou reprise d'apprentissage du modèle sur des mesures, comparaison avec un autre modèle de type haute fidélité représentant la même physique, etc.
    - **Utilisateurs :** connaissant la physique représentée
    - **Exigences :** un ou des indicateurs de fiabilité, des opérateurs de comparaison, etc.

Construire un modèle réduit 3 en combinant deux modèles réduits 1 et 2
----------------------------------------------------------------------

    - **Objet :** si l'on dispose déjà de deux modèles réduits de la même physique ou du même système, élaborer un troisième modèle réduit signifiant sans repasser dans l'espace de représentation des modèles haute fidélité
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Archiver une liste de modèles réduits
-------------------------------------

    - **Objet :** lorsque l'on dispose d'un ou de plusieurs modèles réduits liés, pouvoir en garder une trace informatique que l'on pourra relire, comprendre et utiliser un certain temps plus tard. Cette fonction va au-delà de la simple sauvegarde qui permet seulement de conserver une trace immédiatement réutilisable du modèle réduit, mais n'assure pas sa pérennité ni sa relecture signifiante. Cela consiste aussi à permettre de retrouver un modèle réduit dans un grand nombre de modèles disponibles, d'effectuer un stockage suffisant dans être superflu, etc.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** une norme d'interprétation et un format de stockage avec une pérennité suffisante

Gérer une taille mémoire prescrite pour l'élaboration d'un modèle réduit
------------------------------------------------------------------------

    - **Objet :** lors de l'élaboration d'un modèle réduit, on veut être capable de pouvoir satisfaire à une contrainte de taille mémoire (vive en premier lieu, et disque en second lieu) limitée de manière statique a priori ou dynamique en cours de calcul.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** des moyens de pilotage a priori ou en cours de calculs pour la réduction de modèles, des indicateurs de suivi des calculs

Couvrir avec un modèle réduit un sous-domaine d'usage du modèle haute fidélité
------------------------------------------------------------------------------

    - **Objet :** lorsque l'on dispose d'un modèle réduit, et pour un sous-domaine particulier de l'espace des paramètres, on désire qu'il présente un comportement équivalent au modèle haute fidélité du point de vue de la représentation de la physique
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un domaine d'équivalence de comportement, un ou des indicateurs de fiabilité

Garantir qu'un modèle réduit fonctionne de la même manière que le modèle haute fidélité sur un sous-domaine
-----------------------------------------------------------------------------------------------------------

    - **Objet :** dans ce cas, on désire que le modèle réduit présente le même comportement (par exemple convergence ou divergence de la représentation physique) sur le sous-domaine, et qu'on puisse le garantir
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un domaine d'équivalence de comportement

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

Couplage spatial entre un modèle réduit et un modèle haute fidélité
-------------------------------------------------------------------

    - **Objet :** en disposant d'un modèle haute fidélité sur un domaine complet, on veut utiliser le modèle réduit sur un sous-domaine spatial pour remplacer le modèle haute fidélité en le couplant. Ce cas peut être relié à l'exemple d'utilisation multi-échelles.
    - **Utilisateurs :** Boite Noire
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité, des moyens de couplage spatial entre le modèle réduit et le modèle haute fidélité
    - **Notes :** même cas d'usage que celui appelé par CT "couplage fort avec solveur autre"

Utilisation de tous les calculs intermédiaires existants pour effectuer la réduction
------------------------------------------------------------------------------------

    - **Objet :** dans le cas d'un modèle haute fidélité qui nécessite des calculs intermédiaires (comme par exemple lors d'une convergence itérative), on désire pouvoir utiliser non seulement les résultats convergés, mais aussi les calculs intermédiaires pour établir la réduction du modèle.
    - **Utilisateurs :** sachant établir un modèle réduit
    - **Exigences :** un modèle réduit, un ou des indicateurs de fiabilité

Tableau d'utilisation des cas d'usage par entité
------------------------------------------------

.. tabularcolumns:: |L|L|L|L|L|L|L|L|L|L|L|L|

+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| USE CASE                              |  Participants                                                                            |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
|                                       |  Score | Phi     | CAD   | CT | Sci    | Saf    | SU       | EDF | Cem     | TVL | Min   |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisateur boîte noire                                                                                                          |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Usage d’un modèle réduit en plan      |   6    |   X     |  X    | X  |        |        |          |  X  |   X     |     |  X    |
| d’expérience                          |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisation d’un modèle réduit avec   |        |         |       |    |        |        |          |     |         |     |       |
| des mesures in-situ (en laboratoire,  |   4    |         |  X    | X  |        |        |          |     |   X     |     |  X    |
| sur site de production...)            |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Disposer d’un clone digital basé sur  |        |         |       |    |        |        |          |     |         |     |       |
| un modèle réduit                      |   2    |         |       | X  |        |        |          |     |   X     |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Générer un champ complet à partir     |        |         |       |    |        |        |          |     |         |     |       |
| d’un modèle réduit                    |   4    |         |       |    |        |        |    X     |  X  |   X     |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Permettre la visualisation des        |        |         |       |    |        |        |          |     |         |     |       |
| résultats du modèle réduit            |   5    |         |  X    | X  |        |        |    X     |     |   X     |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Archiver une liste de modèles réduits |   1    |         |       |    |        |        |          |     |   X     |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Gérer une taille mémoire prescrite    |   2    |         |       | X  |        |        |          |     |         |     |  X    |
| pour l’élaboration d’un modèle réduit |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Couvrir avec un modèle réduit un      |        |         |       |    |        |        |          |     |         |     |       |
| sous-domaine d’usage du modèle        |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
| haute fidélité                        |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Garantir qu’un modèle réduit          |        |         |       |    |        |        |          |     |         |     |       |
| fonctionne de la même manière que le  |        |         |       |    |        |        |          |     |         |     |       |
| modèle haute fidélité sur un          |   3    |   X     |       |    |        |        |          | X   |   X     |     |       |
| sous-domaine                          |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Couplage spatial entre un modèle      |        |         |       |    |        |        |          |     |         |     |       |
| réduit et un modèle haute fidélité    |   2    |         |       | X  |        |        |          |     |   X     |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Utilisateur connaissant le modèle complet et/ou la physique                                                                      |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Création d’un modèle réduit pour      |        |         |       |    |        |        |          |     |         |     |       |
| effectuer un plan d’expérience (sans  |        |         |       |    |        |        |          |     |         |     |       |
| exigence de méthode particulière de   |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
| réduction, mais avec un contrôle de   |        |         |       |    |        |        |          |     |         |     |       |
| sa fiabilité)                         |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Comparer un modèle réduit 1 avec un   |        |         |       |    |        |        |          |     |         |     |       |
| modèle haute fidélité 2               |   5    |         |       | X  |        |        |    X     | X   |   X     |     |  x    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Optimisation de loi(s) de comportement|        |         |       |    |        |        |          |     |         |     |       |
| sur structure complexe                |   3    |         |       |    |        |        |          | X   |   X     |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Faire interagir un modèle réduit et   |        |         |       |    |        |        |          |     |         |     |       |
| des opérations de Data Science        |   3    |         |       | X  |        |        |          | X   |   X     |     |       |
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
| Création d’un modèle réduit avec des  |   2    |         |       | X  |        |        |          | X   |   X     |     |       |
| informations provenant de mesures     |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Déduire un modèle réduit 2 à partir   |        |         |       |    |        |        |          |     |         |     |       |
| d’un modèle réduit 1                  |   1    |         |       |    |        |        |          |     |         |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Permettre le calcul multi-échelles ou |        |         |       |    |        |        |          |     |         |     |       |
| multi-physiques de systèmes           |   2    |         |       | X  |        |        |          |     |   X     |     |       |
| représentés par des modèles réduits   |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Permettre la visualisation du modèle  |        |         |       |    |        |        |          |     |         |     |       |
| réduit lui-même                       |   4    |         |       |    |        |   X    |    X     |     |   x     |     |  X    |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+
| Construire un modèle réduit 3 en      |        |         |       |    |        |        |          |     |         |     |       |
| combinant deux modèles réduits 1 et 2 |   2    |         |       | X  |        |        |          | X   |         |     |       |
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
| Utilisation de tous les calculs       |        |         |       |    |        |        |          |     |         |     |       |
| intermédiaires existants pour         |   2    |         |       |    |        |   X    |          | X   |         |     |       |
| effectuer la réduction                |        |         |       |    |        |        |          |     |         |     |       |
+---------------------------------------+--------+---------+-------+----+--------+--------+----------+-----+---------+-----+-------+

Nouveaux cas d'usage potentiels
-------------------------------

Les nouveaux cas d'usage potentiels suivants sont apparus dans les questionnaires.

Pour l'utilisateur boîte noire:

    * utiliser la réduction de modèle dans les problèmes d'optimisation (CADLM, CT, EDF)

    * utiliser la réduction de modèle dans une boucle de calcul d'incertitudes (CT)

    * calculer des quantités mécaniques d'intérêt macroscopiques, par post-traitement (par ex durée de vie) (Mines)

    * charger/ouvrir un modèle réduit (Phiméca). A mettre en lien avec le cas d'usage "Archiver une liste de modèles réduits"

    * utiliser un modèle réduit dans une modélisation système (MBSE, Modelica) (CT, EDF)

    * optimiser le placement des capteurs dans un bâtiment (Cemosis)

Pour l'utilisateur connaissant le modèle complet et/ou la physique:

    * valider la représentativité du modèle (Phiméca): peut-on considérer que c'est le même cas d'usage que "comparer un modèle réduit 1 avec un modèle HF 2" ?

    * accélérer la convergence pour un modèle turbulent de Navier-Stokes (utilisation in-situ) (Sorbonne)

    * calcul de l'erreur entre la solution HF et modèle réduit (Sorbonne) -> de nombreux cas d'usage mentionnent le calcul d'un indicateur de fiabilité, peut-on considérer que celui-ci est un cas d'usage de plus bas niveau que ceux-là ?

Pour l'utilisateur sachant établir le modèle réduit;

    * création d'un modèle réduit à partir d'un DoE déjà disponible (et sans possibilité de faire de nouveaux calculs HF) (CADLM)

    * archiver / sérialiser le modèle pour le transmettre (Phiméca). A mettre en lien avec le cas d'usage "Archiver une liste de modèles réduits"

    * développer dans Mordicus une nouvelle méthodologie de réduction de modèle (Safran) ou apporter des améliorations à une méthode existante

    * créer un modèle réduit à partir d'un nouveau cas métier, et une méthode de réduction existante (Safran, Sorbonne)

    * évaluer le modèle réduit en un point -> cas d'usage de plus bas niveau que certains

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


