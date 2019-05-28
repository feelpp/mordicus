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

Model reduction technique (ROM) allow to tremedously reduce the complexity of parametrized problems by means of treatments of pre-computed "high-dimentional" solutions. The treatment often depends on the nature of the equations underlying the given problem.

Defining the case
^^^^^^^^^^^^^^^^^

Making use of this techniques, the first step consists in specifying the parametrized problem - at least the features ROM techniques depend on - and the possibly available pre-computed "high-dimentional" solutions.

This is achieved by means of **CASE_DATA**, which is the "root" class of the data model, see :numref:`v0_zoom1`. It gathers the numerical description of the physical problem to solve. It defines as attributes the *inputs* and *outputs* that will be made public to the black-box user of the reduced-order model, as well as the available *computed_solutions*, either pre-computed or computed as part of the offline procedure.

.. _v0_zoom1:
.. figure:: images/v0_zoom1.png

In addition, it owns:

 -case_reference       uniquely identifies the case in a catalog, or in all those that were open with this installation of Mordicus
 -case_documentation   (optional) a file documenting the case

Except for this, the case contains all data not subjected to reduction. A **SOLVER_DATASET** object gathers all data to be provided to the external "high-dimentional" solver to reproduce (or merely produce) the solution of such a *nominal* case, i.e. with default values for varying parameters. For almost all solvers, it consists in:

 -instruction_file     a file of instructions that the solver is able to interprete
 -resolution_data      all supplementary data to the main instruction file. 

*Resolution data* have to be readable by the external solver and referenced by Mordicus, so only *ResolutionDataInTypes* are suported: those are the *builtin* data types (i.e. those of C++ or python, not the specific classes in Mordicus), or a file.

So the *SOLVER_DATASET* object owns all data provided to the solver according to which we can not reduce, even if we wanted to. For instance, a purely numerical parameter, or some solver configuration parameter, or a file decribing an initial state.

It references a **FIXED_PARAMETERS** objects that we could have made variable - in the sense that the reduction method is suitable for this, but we chose not to. For instance, a fixed material coefficient. The attributes are:

 -value                the value of fixed parameter
 -ref_insertion_jdd    a string identifier that relates to the main instruction file and says how the value is used

In addition, *SOLVER_DATASET* references an **EXTERNAL_SOLVING_PROCEDURE** object that caracterizes the external solving tool to Mordicus. This object does not represent the solver itself, that shall not be included in Mordicus, but it says how to call it. For this, it has the following attributes:

 -solver_name                  a unique identifier for this installation of this external solver tool
 -solver_version               a string indicating the version of the solver
 -environment_variables        an optional dictionary of environment variables to set before calling
 -root_install_dir             the root install directory of the solver (may be in environment_variables too)
 -solver_call_procedure_type   one of "Python", "shell", "FMI". Channel through which to call the solver
 -postpro_datadriver_callback  a *STANDARD_FUNCTION_DECLARATION*, specifies the expected interface for
                               potential callback in the Mordicus standard that the user may want to call
                               after the solver in order to convert the results to Mordicus data type.


Discrete support: a generalization of the mesh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yet to write





