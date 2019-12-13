.. _viscous_fall:

Chute visqueuse (sous forme de cas d'usage normalisé)
-----------------------------------------------------

:Nom: faire une étude probabiliste d'un modèle de chute d'un solide dans un fluide visqueux, cf `chute visqueuse <http://openturns.github.io/openturns/latest/examples/meta_modeling/viscous_fall_metamodel.html>`_

----

:Objectif (= intention principale du cas d’utilisation): Créer un modèle réduit pour pouvoir échantilloner rapidement le modèle pour dérouler une étude probabiliste

----

:Acteur principal (= celui qui va réaliser le cas d’utilisation): ingénieur R&D en propagation d'incertitudes

----

:Acteurs secondaires (= ceux qui reçoivent des informations à l’issue du cas d’utilisation): ???

----

:Système: dans ce cas, il s'agit d'Openturns `OpenTURNS <http://openturns.org/>`_

----

:Les pré-conditions (= état dans lequel le système doit être pour que le cas d’utilisation démarre): disposer d’une fonction d'évaluation du modèle analytique donnant l'altitude fonction du temps pour une grille de temps donnée, en fonction des paramètres. Cf étapes 1 à 6 de  `chute visqueuse <http://openturns.github.io/openturns/latest/examples/meta_modeling/viscous_fall_metamodel.html>`_. Dans cet exemple, le modèle est analytique, à 4 variables scalaires.

----

:Scénario nominal (= échange d’évènements entre l’acteur et le système):

    #. The user provides the output (time series, on a 1000-point mesh) for a random sampling (2000 samples) of the input parameter

    #. The system computes the Karhunen-Loève modes of the outputs (step 7)
    
           * donnée entrée: tolérance

    #. The system computes the coefficients of the Karhunen-Loève expansion of the samples (step 8)

    #. Assuming each coefficient of the KL expansion is an independent random variable, the system uses polynomial chaos to interpolate them: polynomials are tensorial products on each input variable, with Legendre orthonormal polynomials for input variable with uniform distribution and Hermite orthonormal polynomials for input variable with normal distribution. The direct regression method is used to compute the coefficients of these polynomials, cf `this reference <https://ethz.ch/content/dam/ethz/special-interest/baug/ibk/risk-safety-and-uncertainty-dam/publications/book-chapter/2011-Fiab-08.pdf>`_

    #. The system builds the associated metamodel.

    #. On a validation sampling of reduced size, the user compares the results of the original and meta-models.

