.. _meca_sequential:

Cas test MecaSequential
=======================

Ce cas test vise à valider la méthode POD + quadrature empirique pour les calculs statiques élastoplastiques avec ZSet.

Description du problème physique
--------------------------------

Géométrie, sollicitations et conditions aux limites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On considère un cube de côté 1m, soumis à :

   * un chargement thermique variable, sous forme d'un champ de température variable calculé à partir de résultats d'un précédent calcul thermique
et de fonction d'interpolation en temps donnée sur la figure ...

   * d'une force volumique centrifuge variable calculée depuis l'axe de rotation ... et dont l'intensité est donnée par la fonction temporelle ... 
(insérer une référence vers une image ou une équation);

   * d'une pression variable appliquée sur la surface ... et d'intensité donnée par la fonction temporelle ...

   * afin de bloquer les mouvements de corps rigide, la face ... est bloquée selon :math:`X`, 
la ligne ... selon :math:`Y` et le point :math:`O` selon :math:`Z`

.. .. figure:: chemin/vers/une/jolie/figure.png
..
..     Titre de la figure
    

Hypothèses de modélisation
~~~~~~~~~~~~~~~~~~~~~~~~~~

Les équations d'équilibre quasi-statique du solide déformable sont résoluées, en petites transformations.

Comportement du milieu
~~~~~~~~~~~~~~~~~~~~~~

Le matériau est élasto-visco-plastique à écrouissage mixte non linéaire. La partie visqueuse suit la loi de Norton. Il est spécifié par le fichier mat.

Stratégie de réduction
----------------------

Entrées variables et sorties observées
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ce cas test est une simple *reproduction de solution*: on ne fait pas varier de paramètres. 

L'objectif (qui sera fait dans d'autres tests) est de faire varier les champs de température d'entrée 
(ou la fonction d'interpolation temporelle, je ne sais plus, à vérifier auprès de Fabien).

Les sorties observées sont des *champs*: le champ de déplacement primal ``U`` et le champ de plasticité cumulée :math:`p` (appelé ``evrcum``).

Compression des données
~~~~~~~~~~~~~~~~~~~~~~~

La base réduite est générée par POD par la méthode des snapshots: méthode ``CompressData`` du noyau.

Compression des opérateurs
~~~~~~~~~~~~~~~~~~~~~~~~~~

La compression des opérateurs est faite par la méthode de quadrature empirique ECM du module Safran.

Mise en oeuvre numérique
------------------------

Format des résultats et codes utilisés
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Les snapshots sont générés avec ZSet et lus depuis le format ZSet.

.. _MecaSequential_verification_qualite_approx:

Vérification de la qualité d'approximation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. cette section est obligatoire

La qualité de la *compression des données* est faite en comparant les snapshots originaux et leur projection sur la base réduite générée.
On vérifie que :math:`\dfrac{| u - \sum_{i=1}^N \left( u, v_i\right) v_i|}{|u|} \le 1 \times 10^{-5}`. Idem pour :math:`p`.

La qualité de la procédure complète est faite en calculant la norme :math:`\mathcal{l}_2` de l'erreur entre solution complète et solution réduite.
On vérifie que :math:`\dfrac{| u - \sum_{i=1}^N \gamma_i^u v_i|}{|u|} \le 1 \times 10^{-5}`, avec :math:`\gamma_i` les coefficients issus de la résolution réduite.

Code - phase offline
--------------------

Liste des imports nécessaires à la phase offline de cet exemple:

.. code-block:: python

    from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
    from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
    from Mordicus.Core.Containers import ProblemData as PD
    from Mordicus.Core.Containers import CollectionProblemData as CPD
    from Mordicus.Core.Containers import Solution as S
    from Mordicus.Modules.Safran.FE import FETools as FT
    from Mordicus.Modules.Safran.DataCompressors import FusedSnapshotPOD as SP
    from Mordicus.Modules.Safran.OperatorCompressors import Mechanical
    import numpy as np    

Vient ensuite une phase de déclaration des noms de fichiers et des dimensions liées aux maillages et aux solutions:

.. code-block:: python

   meshFileName = "MecaSequential/cube.geof"
   solutionFileName = "MecaSequential/cube.ut“
   meshReader = ZMR.ZsetMeshReader(meshFileName)
   solutionReader = ZSR.ZsetSolutionReader(solutionFileName)
   mesh = meshReader.ReadMesh()
   numberOfNodes = mesh.GetNumberOfNodes()
   numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
   nbeOfComponentsPrimal = 3
   nbeOfComponentsDual = 6

On réalise ensuite la partie de l'algorithme ECM qui dépend uniquement du maillage:

.. code-block:: python

   operatorPreCompressionData = Mechanical.PreCompressOperator(mesh)

On déclare ensuite l'objet ``Solution`` et on le peuble à partir de solutions ZSet pré-calculées:

.. code-block:: python

   outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()
   solutionU = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
   solutionSigma = S.Solution("sigma", nbeOfComponentsDual, numberOfIntegrationPoints, primality = False)
   solutionEvrcum = S.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
   for time in outputTimeSequence:
      solutionU.AddSnapshot(solutionReader.ReadSnapshot("U", time, nbeOfComponentsPrimal, primality=True), time)
      solutionSigma.AddSnapshot(solutionReader.ReadSnapshot("sig", time, nbeOfComponentsDual, primality=False), time)
      solutionEvrcum.AddSnapshot(solutionReader.ReadSnapshotComponent("evrcum", time, primality=False), time)

On déclare ensuite les objets ``CollectionProblemData`` et ``ProblemData`` qui permettront d'agréger les ``Solution`` précédemment construites
de façon standard dans Mordicus.

.. code-block:: python

   problemData = PD.ProblemData("MecaSequential")
   problemData.AddSolution(solutionU)
   problemData.AddSolution(solutionSigma)
   problemData.AddSolution(solutionEvrcum)
   collectionProblemData = CPD.CollectionProblemData()
   collectionProblemData.addVariabilityAxis('config', str, description="dummy variability")
   collectionProblemData.defineQuantity("U", "displacement", "m")
   collectionProblemData.defineQuantity("sigma", "stress", "Pa")
   collectionProblemData.defineQuantity("evrcum", "accumulated plasticity", "")
   collectionProblemData.AddProblemData(problemData, config="case-1")

On calcule ensuite l'opérateur de corrélation des snapshots de daplacement (indentifiant ``U``).

.. code-block:: python

   snapshotCorrelationOperator = {"U":FT.ComputeL2ScalarProducMatrix(mesh, 3)}

On calcule ensuite la base réduite sur ``U``  par POD, avec l'opérateur de corrélation :math:`L_2 (\Omega)`, et la base POD sur :math:`p`
afin de pouvoir ultérieurement réaliser la Gappy POD sur cette variable.

.. code-block:: python

   SP.CompressData(collectionProblemData, "U", 1.e-6, snapshotCorrelationOperator["U"])
   SP.CompressData(collectionProblemData, "evrcum", 1.e-6)

On calcule ensuite les coordonnées réduites des snapshots sur la base POD:

.. code-block:: python

   collectionProblemData.CompressSolutions("U", snapshotCorrelationOperator["U"])

On vérifie ensuite la qualité de la *compression des données* comme expliqué en MecaSequential_verification_qualite_approx_.

.. code-block:: python

   reducedOrderBasisU = collectionProblemData.GetReducedOrderBasis("U")
   CompressedSolutionU = solutionU.GetCompressedSnapshots()
   compressionErrors = []
   for t in outputTimeSequence:
      reconstructedCompressedSolution = np.dot(CompressedSolutionU[t], reducedOrderBasisU)
      exactSolution = solutionU.GetSnapshot(t)
      norml2ExSol = np.linalg.norm(exactSolution)
      if norml2ExSol != 0:
         relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)/norml2ExSol
      else:
         relError = np.linalg.norm(reconstructedCompressedSolution-exactSolution)
         compressionErrors.append(relError)

On réalise la fin de l'algorithme ECM afin de déterminer le schéma de quadrature empirique:

.. code-block:: python

   Mechanical.CompressOperator(collectionProblemData, operatorPreCompressionData, mesh, 1.e-5,
   listNameDualVarOutput = ["evrcum"], listNameDualVarGappyIndicesforECM = ["evrcum"])

Enfin, au terme de la phase *offline*, on sauvegarde le modèle de données de Mordicus, contenant notamment les résultats de la phase offline,
afin de pouvoir le recharger lors de la phase *online*:

.. code-block:: python

   SIO.SaveState("collectionProblemData", collectionProblemData)
   SIO.SaveState("snapshotCorrelationOperator", snapshotCorrelationOperator)

Code - phase online
-------------------

Liste des imports nécessaires à la phase online de cet exemple:

.. code-block:: python

   from Mordicus.Modules.Safran.IO import ZsetInputReader as ZIR
   from Mordicus.Modules.Safran.IO import ZsetMeshReader as ZMR
   from Mordicus.Modules.Safran.IO import ZsetSolutionReader as ZSR
   from Mordicus.Modules.Safran.IO import ZsetSolutionWriter as ZSW
   from Mordicus.Core.Containers import ProblemData as PD
   from Mordicus.Core.Containers import Solution as S
   from Mordicus.Modules.Safran.FE import FETools as FT
   from Mordicus.Modules.Safran.IO import PXDMFWriter as PW
   from Mordicus.Modules.Safran.OperatorCompressors import Mechanical as Meca
   from Mordicus.Core.IO import StateIO as SIO
   import numpy as np

On lit ensuite les données sauvergardées à la fin de la phase online:

.. code-block:: python

   collectionProblemData = SIO.LoadState("collectionProblemData")
   operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
   snapshotCorrelationOperator = SIO.LoadState("snapshotCorrelationOperator")

   operatorCompressionData = collectionProblemData.GetOperatorCompressionData()
   reducedOrderBases = collectionProblemData.GetReducedOrderBases()

Vient ensuite une phase de déclaration des noms de fichiers et des dimensions liées aux maillages et aux solutions, comme lors de la phase online:

.. code-block:: python

   folder = "MecaSequential/"
   inputFileName = folder + "cube.inp"
   inputReader = ZIR.ZsetInputReader(inputFileName)

   meshFileName = folder + "cube.geof"

On lit ensuite le maillage (requis dans le cas où la *donnée variable* n'est pas un paramètre réel):

.. code-block:: python

   mesh = ZMR.ReadMesh(meshFileName)
   
On définit ensuite un objet ``ProblemData`` qui portera le résultat de la résolution online.

.. code-block:: python

   onlineProblemData = PD.ProblemData("Online")
   onlineProblemData.SetDataFolder(folder)

On lit ensuite la séquence temporelle et la loi de comportement depuis le fichier input ZSet.
Ce sont des *données fixes* qui seront utiles pour la résolution online.

.. code-block:: python

   timeSequence = inputReader.ReadInputTimeSequence()
   constitutiveLawsList = inputReader.ConstructConstitutiveLawsList()
   onlineProblemData.AddConstitutiveLaw(constitutiveLawsList)

On lit ensuite le chargement et la condition initiale depuis le fichier input ZSet, on on les réduit en les projetant sur la base POD:

.. code-block:: python

   loadingList = inputReader.ConstructLoadingsList()
   onlineProblemData.AddLoading(loadingList)
   for loading in onlineProblemData.GetLoadingsForSolution("U"):
      loading.ReduceLoading(mesh, onlineProblemData, reducedOrderBases, operatorCompressionData)

   initialCondition = inputReader.ConstructInitialCondition()
   onlineProblemData.SetInitialCondition(initialCondition)

   initialCondition.ReduceInitialSnapshot(reducedOrderBases, snapshotCorrelationOperator)

On calcule ensuite la solution réduite en utilisant le solveur éléments finis *online* recodé par Safran:

.. code-block:: python

   onlineCompressedSolution, onlineCompressionData = Meca.ComputeOnline(onlineProblemData, timeSequence, operatorCompressionData, 1.e-8)

On calcule les coordonnées généralisées de :math:`p` sur la base POD de :math:`p` (gappy POD):

.. code-block:: python

   onlineEvrcumCompressedSolution, errorGappy = Meca.ReconstructDualQuantity("evrcum", operatorCompressionData, onlineCompressionData, timeSequence = list(onlineCompressedSolution.keys()))

On finalise la déclarations des dimensions:

.. code-block:: python

   numberOfIntegrationPoints = FT.ComputeNumberOfIntegrationPoints(mesh)
   nbeOfComponentsPrimal = 3
   numberOfNodes = mesh.GetNumberOfNodes()
   solutionFileName = folder + "cube.ut"
   solutionReader = ZSR.ZsetSolutionReader(solutionFileName)
   outputTimeSequence = solutionReader.ReadTimeSequenceFromSolutionFile()

Afin de pouvoir comparer solution réduite et solution complète, on déclare un objet ``Solution`` et on lit les données des solutions ZSet pré-calculées:

.. code-block:: python

   solutionEvrcumExact = S.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
   solutionUExact = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
   for t in outputTimeSequence:
      evrcum = solutionReader.ReadSnapshotComponent("evrcum", t, primality=False)
      solutionEvrcumExact.AddSnapshot(evrcum, t)
      U = solutionReader.ReadSnapshot("U", t, nbeOfComponentsPrimal, primality=True)
      solutionUExact.AddSnapshot(U, t)

On crée à présent des objet ``Solution`` correspondant à la résolution réduite.
On leur affecte les coordonnées réduites qui résultent de la phase online, puis on reconstruit une solution sur tout le maillage.

.. code-block:: python

   solutionEvrcumApprox = S.Solution("evrcum", 1, numberOfIntegrationPoints, primality = False)
   solutionEvrcumApprox.SetCompressedSnapshots(onlineEvrcumCompressedSolution)
   solutionEvrcumApprox.UncompressSnapshots(reducedOrderBases["evrcum"])
   solutionUApprox = S.Solution("U", nbeOfComponentsPrimal, numberOfNodes, primality = True)
   solutionUApprox.SetCompressedSnapshots(onlineCompressedSolution)
   solutionUApprox.UncompressSnapshots(reducedOrderBases["U"])

On calcule enfin l'erreur liée à la réduction afin de valider la qualité d'approximation:

.. code-block:: python

   ROMErrorsU = []
   ROMErrorsEvrcum = []
   for t in outputTimeSequence:
      exactSolution = solutionEvrcumExact.GetSnapshotAtTime(t)
      approxSolution = solutionEvrcumApprox.GetSnapshotAtTime(t)
      norml2ExactSolution = np.linalg.norm(exactSolution)
      if norml2ExactSolution > 1.e-10:
         relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
      else:
         relError = np.linalg.norm(approxSolution-exactSolution)
      ROMErrorsEvrcum.append(relError)

      exactSolution = solutionUExact.GetSnapshotAtTime(t)
      approxSolution = solutionUApprox.GetSnapshotAtTime(t)
      norml2ExactSolution = np.linalg.norm(exactSolution)
      if norml2ExactSolution > 1.e-10:
         relError = np.linalg.norm(approxSolution-exactSolution)/norml2ExactSolution
      else:
         relError = np.linalg.norm(approxSolution-exactSolution)
      ROMErrorsU.append(relError)

On exporte enfin les prédictions réduites au format ZSet:

.. code-block:: python

   onlineProblemData.AddSolution(solutionUApprox)
   ZSW.WriteZsetSolution(mesh, meshFileName, "reduced", collectionProblemData, onlineProblemData, "U")