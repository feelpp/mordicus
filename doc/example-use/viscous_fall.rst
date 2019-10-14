.. _viscous_fall:

Chute visqueuse
---------------

Cet exemple de `chute visqueuse <http://openturns.github.io/openturns/latest/examples/meta_modeling/viscous_fall_metamodel.html>`_
est tiré de la documentation d'`OpenTURNS <http://openturns.org/>`_.
Cet exemple illustre la création d'un modèle réduit pour pouvoir échantillonner
rapidement le modèle pour dérouler une étude probabiliste (analyse de sensibilité, simulation, etc).

Le modèle est analytique, à 4 variables d'entrées scalaires,
1 variable de sortie scalaire et portée par un maillage temporel à 100 points.
La méthode de décomposition utilisée pour construire la base fonctionnelle est Karhunen-Loeve par SVD.
La méthode d'interpolation est le chaos polynomial.

L'acteur principal est l'ingénieur R&D en propagation d'incertitudes.
