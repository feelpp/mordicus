.. _class_diagram:

Description of version v0 of the datamodel
==========================================

Foreword
--------

This section summarizes the *domain model* for the scope that Mordicus should cover. It is not (yet) an *implementation model*: it does not say how things will effectively be implemented in Mordicus, though it gives a first hint. For instance, a *classifier* in this diagram will not necessarily lead to a *class* in Mordicus. But it does describe the structure of data that will be employed in Mordicus.

This *domain model* identifies all data Mordicus will need direct access to. It encompasses the whole information needed to get the data science methods in Mordicus to work. Therefore, information about the modeled physics, or the PDE solving techniques scarcely appear in this data model. When not needed by the data science method, this information is internal to the solver or a custom method that Mordicus will call, and therefore it does appear in the data model.

Overview of the model
---------------------

Here is the *domain model* under the form of a class diagram:

.. image:: images/REFERENCE_CLASS_DIAGRAM.png

For modification in Modelio, the zip file is available at this link :download:`zip <data/Mordicus_Datamodel.zip>`.

Data simulation part
--------------------

Yet to write
