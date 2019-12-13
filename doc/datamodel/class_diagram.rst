.. _class_diagram:

Description of version v0 of the datamodel
==========================================

Foreword
--------

This section summarizes the *domain model* of the scope that Mordicus should cover. It is not (yet) an *implementation model*: it does not say how things will effectively be implemented in Mordicus, though it gives a first hint. For instance, a *classifier* in this diagram will not necessarily lead to a *class* in Mordicus. But it does describe the structure of data that will be employed in Mordicus.

This *domain model* identifies all data Mordicus will need direct access to. It puts together the information pieces needed to get data science methods in Mordicus to work. Therefore, information about the modeled physics or about the PDE solving techniques scarcely appear in this data model. When not needed by the data science method, this information is deemed internal to the solver, or internal to a custom method called by Mordicus, and therefore it does appear in the data model.

Overview of the model
---------------------

The full *domain model* is presented under the form of a class diagram on :numref:`full_model`. In hard to read in this state, so we'll go into details in the coming paragraphs, and the data model is available for interactive consultation on the open software Modelio, with the zip file at this link :download:`zip <data/Mordicus_Datamodel.zip>`.

.. _full_model:
.. figure:: images/REFERENCE_CLASS_DIAGRAM.pdf

   Full representation of the data model

Data simulation part
--------------------

Model reduction technique (ROM) allow a tremendous reduction of the complexity of parametrized problems, by means of data treatments of pre-computed "high-dimentional" solutions. The treatment often depends on the nature of the equations underlying the given problem.

.. _case_data:

Defining the case
^^^^^^^^^^^^^^^^^

Making use of this techniques, the first step consists in specifying the parametrized problem - at least the features ROM techniques depend on - and the possibly available pre-computed "high-dimentional" solutions.

This is achieved by means of **CASE_DATA**, which is the "root" class of the data model, see :numref:`v0_zoom1`. It gathers the numerical description of the physical problem to solve. It defines as attributes the *inputs* and *outputs* that will be made public to the black-box user of the reduced-order model, as well as the available *computed_solutions*, either pre-computed or computed as part of the offline procedure. These will be detailed in io_indexing_.

.. _v0_zoom1:
.. figure:: images/v0_zoom1.pdf

    Zoom on the case definition

In addition, it owns:

 -case_reference       uniquely identifies the case in a catalog, or in all cases that were once opened with this installation of Mordicus
 -case_documentation   (optional) a file documenting the case

Except for this, the case contains all data not subjected to reduction. A **SOLVER_DATASET** object gathers all data to be provided to the external "high-dimentional" solver to reproduce (or merely produce) the solution of such a *nominal* case, i.e. with default values for varying parameters. For almost all solvers, it consists in:

 -instruction_file     a file of instructions that the solver is able to interprete
 -resolution_data      all supplementary data to the main instruction file. 

*Resolution data* have to be readable by the external solver and referenced by Mordicus, so only *ResolutionDataInTypes* are supported: those are the *builtin* data types (i.e. those of C++ or python, not the specific classes in Mordicus), or a file.

So the *SOLVER_DATASET* object owns all data provided to the solver according to which we can not reduce, even if we wanted to. For instance, a purely numerical parameter, or some solver configuration parameter, or a file decribing an initial state.

It references a **FIXED_PARAMETERS** object that could have varied - in the sense that the reduction method would be suitable for this, but we chose to keep it fixed. For instance, a fixed material coefficient. The attributes are:

 -value                the value of fixed parameter
 -ref_insertion_jdd    a string identifier that relates to the main instruction file and says how the value is used

 .. todo::
     In the *domain model* as drawn up, *FIXED_PARAMETER* and *VARIABLE_PARAMETER* only supports real values. It's important in the future to extend this at least to: input time signal and discrete support. Indeed, variable input time signals are the common varying data for a family of reduction techniques mainly for linear problems. As for discrete supports, they come into play in advanced method with a non-parametrized variable geometry. It's important to support both in Mordicus, which does seems too complicated given that the corresponding objects exist (respectively *QUANTITY_OF_INTEREST* and *DISCRETE_SUPPORT* to be explained later).

In addition, *SOLVER_DATASET* references an **EXTERNAL_SOLVING_PROCEDURE** object that caracterizes the external solving tool to Mordicus. This object does not represent the solver itself, that shall not be included in Mordicus, but it says how to call it. For this, it has the following attributes:

 -solver_name                  a unique identifier for this installation of this external solver tool
 -solver_version               a string indicating the version of the solver
 -environment_variables        an optional dictionary of environment variables to set before calling
 -root_install_dir             the root install directory of the solver (may be in environment_variables too)
 -solver_call_procedure_type   one of "Python", "shell", "FMI". Channel through which to call the solver
 -procedure_to_call_solver     the file implementing the calling procedure. It is the shell or python script calling the external tool.
 -postpro_datadriver_callback  a *STANDARD_FUNCTION_DECLARATION*, specifies the expected interface for
                               potential callback in the Mordicus standard that the user may want to call
                               after the solver, in order to convert the results to Mordicus data type.


Discrete support: a generalization of the mesh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Among the objects assembled by *CASE_DATA*, one deserves special attention: the **DISCRETE_SUPPORT**. The numerical description of the problem to solve almost always relies on *discrete supports*, at least for time and space, that play specific roles during the reduction process and for the reconstruction of reduced results.

The *DISCRETE_SUPPORT* is a common data type to specify *definition domains* in space, time or parameter. *Definition domains* may also be defined by a cartesian product of discrete supports implicitely: the result *discrete support* of the cartesian product is not computed, it would be too heavy in memory.

.. _v0_zoom2:
.. figure:: images/v0_zoom2.pdf

   Zoom on the notion of discrete support

.. todo::
   Represent this ability to do cartesian products on the datamodel by a reference of *DISCRETE_SUPPORT* onto itself.

In this way, space, time and parameter-based *discrete supports* are instances of the same class. For instance, a 1D space mesh and a time discrete interval are represented by the same data structure. Nevertheless, *DISCRETE_SUPPORT* contains attributes (see :numref:`v0_zoom2`):

 -type                    into "space", "time", "parameter", "tensorial_product". Indicates the quantity the discrete support relates to.
 -topological_dimension   the dimention :math:`d` of the surrouding space, or the number of reals to give to define a point.
 -has_been_read           because mesh files can be heavy, their loading in memory can be delayed until needed:
                          this attributes tells wether the discrete support has been loaded in memory or it still has to be imported from a file
 -has_been_built          tells if the discrete support has been explicitely built or exists as a definition (e.g. "All points between 0 and 10 with a stride of 0.5")

.. todo::
    For not yet loaded mesh, add a file attribute.

A *DISCRETE_SUPPORT* is a hierarchy of entities in :math:`\mathbb{R}^N` (nodes, edges, faces,volumes), starting at the lowest level (dimension 0 objects) with *nodes* or *points*. **NODES** are defined straight by their *coordinates* attribute, whereas **POINTS** take their definition from a higher-level entity: consider the center of a finite-volume cell or a Gauss point (defined from a reference finite element) for instance.

The discrete support is conceptually a tree of **ENTITIES**, represented in the class diagram according to the composite design pattern (see :numref:`v0_zoom2`): leaf *entities* are nodes, and higher-level *entities* are defined from them on. Let take the example of a 3D mesh: in most cases, the volumes (level 3 entities) are defined straight from the nodes, intermediate entities (edges, surfaces) are omitted. They would be heavy in memory, and can be reconstructed by the viewer from the ordered list of "child" nodes. As for us, the support is merely defined as a tree of entities under the conditions that parent be at a strictly higher level than children, but no further condition. So, an entity has 2 attributes:

 -dim                          the "dimension" or "level" of the entity (0 for points and nodes, 1 for edges, 2 for faces, 3 for volumes)
 -reference_element_topology   a string qualifying the topology of the element. For instance: "triangle_3nodes", "triangle_6nodes", "hexaedron_8nodes" etc.
                               
 
 This *reference_element_topology* attribute allows to call a finite element logics, possibly coded by Mordicus modules, specifically for each type of element, for instance for specific reduction methods such as hyper-reduction. However, this logics is internal to such a module and the underlying internal data do not appear in Mordicus, which only needs to provide the module with a referenced element topology in a common list for each element in the mesh.

.. note::
    It is conceptually attractive to define each entity exclusively from the next lower level (edges from nodes, faces from edges etc), but as said this would imply heavy and unnecessary information: there is seldom the need, for instance, to define all faces of the mesh in the model. On the other side, it is comfortable for some methods to have faces available in the mesh, hence the choice to prescribe no further condition.

A *DISCRETE_SUPPORT* has the ability to tag groups of entities.

.. todo::
    Represent this ability in class diagram.

Only those features of *POINT* that persist after the local treatment of a finite element or a cell are published as attributes, as potential useful data to reduction procedures. For instance, for a Gauss point in the context of a finite element method, the reference coordinate, reference shape functions values and reference quadrature weights are *not* kept. They may be recovered upon request from the element characteristics, in particular *reference_element_topology*. But the real coordinates and quadrature weights are kept in a persistent *POINT* object: it will serve as a shortcut to reduction procedures such as empirical quadrature, which would then have not need to dig into the finite element logics.

.. _types_of_result:

Quantities of interest, fields and unknowns: the 3 kinds of results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The specified *outputs* to *CASE_DATA* may be of 3 kinds, see :numref:`v0_zoom3`, ranging from "closer to business user" to "closer to mathematical techniques":

    * quantities of interest

    * field

    * vector of unknowns.

.. _v0_zoom3:
.. figure:: images/v0_zoom3.pdf

   Zoom on the 3 kinds of results, and their structure in relation to the discrete support

The **QUANTITY_OF_INTEREST** class aims at equally representing signals from "physical" or "numerical" sensors of the case. In attribute *series_value*, it bears one value (possibly a vector, or a tensor) for each index in the indexing system of the case. It may originate from a post-processing of the simulation (for instance, flow through a section) or from experimental data. In other words, it is an observation on the system. Many times, the end business user is only interested in a few *quantities of interest* among the results of a simulation.

The semantic information giving context to these values is contained in the **QUANTITY_OF_INTEREST_STRUCTURE** object. That information is about:

    * the *physical nature* of the quantity, via a link to exactly one *PHYSICAL_QUANTITY* object,

    * the *origin* of data (the "sensor", in a broad sense, and its *localisation*),

    * the discrete support to associate with the series of data. It has to be 1D. In most cases, it represents *time* sampling, but not always: there are series based on frequencies or energy levels.

To support this information, *QUANTITY_OF_INTEREST_STRUCTURE* owns the following attributes:

 -experimental_or_simulation         does data originate from a physical sensor or numerical observation (post-processing)?
 -sensor_name                        a free label meant to use as a reference of the physical sensor. It needs not be unique, so that
                                     the same label can be used for different quantity measured at the same sensor location, or even
                                     by the same device (displacement and velocity, for instance)
 -integral_or_local                  in the simulation case, is the quantity of interest a punctual value of a field or is it obtained
                                     by an integral operation ?
 -description                        free field to describe the *type of measure*
 -series_or_value                    is the value a series (in most case) or just a value. In the latter case, no discrete support
                                     should be provided.


.. note::
    It is debatable that the *experimental_or_simulation* should be supported by *QUANTITY_OF_INTEREST_STRUCTURE*. One might want to have the same structure both for experimental and simulation data, in order to relate and compare them easily. For instance, for PBDW method, it is appreciable to know at a glance what the localisation operation is to get the numerical counterpart of an experimental signal.

.. todo::
    Put *experimental_or_simulation* in *QUANTITY_OF_INTEREST* instead ?

About the nature of the quantity, a *QUANTITY_OF_INTEREST_STRUCTURE* is associated with a single **PHYSICAL_QUANTITY**, an object that describes its physical *nature*. A physical quantity is composed of:

 -label                         explicit of the nature of the quantity. May be chosen in a preexisting list 
                                ("displacement", "velocity", "first Piloa-Kirschhoff stress"...) or a free value.
                                The preexisting list may be provided straight from other norms (CGNS) or systems of measurements.
                                One can never be exhaustive, so the user should still be able to provide a value not in a closed list.
 -unit                          Tells in what unit data is expected to be provided. Idem: adopt a system of measurement (SI, LH...) 
                                of one or the other norm.                      
 -tensor_order                  the order of the provided tensor values. 0 for scalars, 1 for vectors, 2 for matrices etc.
                                Not to be confused with the number of components in each direction,
                                that most of the times depends on the order of the underlying space (i.e.
                                the *topological dimension* N of the spatial discrete support.
 -extensive_or_intensive        Is the quantity intensive or extensive.
 -available_components          A exhaustive list with the names of possible component names for each value (for vectors and tensors).
                                For instance, for velocities, it will be 'Vx', 'Vy', 'Vz'


As for the support of the series of data, a series of data is nothing but a field with a support of topological dimension 1. So its structure is a special case of the *FIELD_STRUCTURE* to be seen next.

The **FIELD** class represents a set of "homogeneous" values (values corresponding to the same *PHYSICAL_QUANTITY*) spread out over a multi-dimensional discrete support. The physics of fields classically lays its interest in determining fields defined as a function of space, say :math:`f(\mathbf{X})`, with :math:`\mathbf{X}` the spatial coordinate. This is a continuous notion that needs a discrete representation to be usable by a computer. For this, an approximation space is used which consists in a finite combination of basis functions over the spatial domain :math:`\Omega`.

In all PDE discretizations methods, each coefficient related to a basis function is typically associated to an entity of the discrete support: in "standard" finite-volumes, that would be the center of the cells, in Lagrange or Hermite finite elements the nodes of the mesh, in some discontinuous Galerkin methods the edges and volumes etc.

These associations allow to build a discrete representation of the field under the form of a *vector of value* attribute qualified by a **FIELD_STRUCTURE**.

Following this, the *FIELD_STRUCTURE* references:

    * a single discrete support through *support* attribute;

    * a single *PHYSICAL_QUANTITY* through *quantity* attribute.

In addition to the expected size (*vector_size* attribute) of the vector of values, the *FIELD_STRUCTURE* is composed of *VALUE_SUPPORT*, each of which associates an index in the vector (*value_index* attribute) with an *entity* of the *discrete support*.

**VALUE_SUPPORT** has thus the following attributes:

 -value_index                    the index of the value of the first component associated with the entity
 -number_actual_components       the number of assigned components of the field at this entity
 -actual_components              the list of these assigned components, to be chosen among the *available_components* 
                                 of the *PHYSICAL_QUANTITY* of the field structure

The *FIELD_STRUCTURE* is also endowed with a *entity2validex* attribute, which provides the reverse connection of *value supports*: for a given entity, it returns the *value supports* relying on it. Through that information is conceptually redundant (it could be built from a reverse analysis of the *value supports*), it has to be kept in memory, and maintained up to date, for obvious performance purposes.

With this in mind, let us come back to the *localisation* description of *QUANTITY_OF_INTEREST_STRUCTURE*. For this, a new **RESTRICTION_FIELD_STRUCTURE** object is introduced. This object is used to qualify a vector of values that does not correspond to a full-dimensional field, but to the coordinates in a basis of a **subspace** of the original approximation space. There is a need for this in many circumstances:

    * performing DOF elimination (for instance a wall boundary condition in a CFD computation),
      
    * locating a sensor, specifying how to derive a *quantity of interest* from a *field*,
      
    * and obviously representing the reduced coordinates with respect to empirical modes.

The informations contained in *RESTRICTION_FIELD_STRUCTURE* allow to build a :math:`\mathbf{Z} \in \mathbb{R}^{N \times n}` matrix, that link the coordinates :math:`\mathbf{u} \in \mathbb{R}^N` of the full-space basis with the coordinates :math:`\mathbf{a} \in \mathbb{R}^n` in the reduced-space basis. This relation is:

    * typically :math:`\mathbf{u} = \mathbf{Z} \mathbf{a}` for DOF elimination, with :math:`\mathbf{Z}` a basis of the null-space of the the constraint matrix :math:`\mathbf{B}` (i.e. such that :math:`\mathbf{Z}` has full rank and :math:`\mathbf{B} \mathbf{Z} = 0`;

    * typically :math:`\mathbf{a} = \mathbf{Z}^T \mathbf{u}` to reproduce a sensor's signal from a field;

    * typically :math:`\mathbf{u} = \mathbf{Z} \mathbf{a}` for reduced coordinates with respect to modes, with :math:`\mathbf{Z}` the matrix of modes.

The full-space structure associated with :math:`\mathbf{u}` is provided with the *reference_field_structure* attribute. To support the above cases, the *RESTRICTION_FIELD_STRUCTURE* possesses a *left_or_right_Z* attribute that says whether the built :math:`\mathbf{Z}` matrix is defined as :math:`\mathbf{u} = \mathbf{Z} \mathbf{a}` (left) or :math:`\mathbf{a} = \mathbf{Z}^T \mathbf{u}` (right).

The columns of the Z-matrix can be defined:

    * as *FIELDS* by the *Z_columns* attribute,

    * as *VALUE_SUPPORTS* by the *trivial_Z_columns* attribute, that defines columns of the form :math:`\begin{pmatrix} \vdots \\ 0 \\ 1 \\ 0 \\ \vdots \end{pmatrix}` 

The *group* attribute allows to build a right :math:`\mathbf{Z}`-vector allowing to integrate the field over that group.

.. todo::
    Add attribute *excluded_supports* that would allow to include rather than exlude all *value supports* not specified, so that we can define a large Z by exclusion of some dofs, that corresponds to a few entities implied in linear constraints.

The third kind of result is the **VECTOR_OF_UNKNOWNS** class. This is often the primal unknown of the solver, the "state vector" (vector of discrete state variables) that the problem must determine and that may blend unknowns of different units: for instance, think of FSI cases with displacement, pressures etc. The values are contained in a *vector_of_doubles* attribute, qualified by a **VECTOR_OF_UNKNOWNS_STRUCTURE** class. This structure indicates, among the unknowns:

    * which ones correspond to *FIELD* values;

    * which one correspond to something else, i.e. *QUANTITY_OF_INTEREST* with or without associated localization of the discrete support. For instance, an algebraic Lagrange multiplier would have no link to the discrete support.

This is done by means of the following attributes:

 -primal_fields            an **ordered** list of fields, some values of which form part of the unknown vector
 -primal_qofs              an ordered list of quantities of interest, some values of which form part of the unknown vector
 -index2field              for an index in the *vector_of_doubles*, returns the field or quantity of interest it corresponds (remember these were ordered)
 -index2fieldindex         for an index in the *vector_of_doubles*, returns the corresponding index in the *field structure*

In addition to that, a *field_fieldindex2index* array is also provided as an attribute. For an input (field number, index in field structure), it returns the index in the unknown structure. Though this could be build from reverse analysis of the above, it has to be kept in memory and up-to-date for obvious performance purposes.

Say there are :math:`\mathcal{N}` unknowns. The same way we did for *RESTRICTION_FIELD_STRUCTURE*, we may be able to define a restriction mechanism *RESTRICTION_UNKNOWNS_STRUCTURE* to describe smaller vectors of unknows representing coordinates in subspaces of :math:`\mathbb{R}^{\mathcal{N}}`, based on *vector of unknowns* representing Z-columns. For the sake of clarity, int is not represented on the current data model.

.. _io_indexing:

Description of inputs and outputs, indexing mechanism
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As was said in case_data_, the *CASE_DATA* object includes information about the *model* to be reduced. In other words, it has to describe the input/output of the transfer function, a reduced representation of which which be built by a "model reduction user", see :numref:`v0_zoom4`.

.. _v0_zoom4:
.. figure:: images/v0_zoom4.pdf

    Zoom on the input, outputs and indexing mechanism of the case

For this, the parameters according to which reduction will take place are defined as instances of the **VARIABLE_PARAMETERS** class. They have attribute:

 -name                         unique to identify the parameter in a function defining a definition domain, for instance
 -ref_insertion_jdd            as in case_data_, a string identifier that says how the the main instruction file of the external solver is affected by a change of this parameter
 -nature                       references a *PHYSICAL_QUANTITY*, thus giving the physical nature of the parameter and its unit

For a given case, these parameters are allowed to vary within a definition domain, which is represented by a **SUPPORT_INDEXATION** class. This is represented by attributes:

 -domain_axes                  **ordered** backward references to the parameters (possibly only by a name), in order to define the axes of the underlying parameter space
 -cartesian_bounds             for an axis, defines bounds for the parameters. The domain is then defined by cartesian product with the others.
 -bound_function               under the form of a *FUNCTION_OF_PARAMETER*, provides function :math:`f (\mu)` so that the parameter is within domain if :math:`f (\mu) \leq 0`

The *SUPPORT_INDEXATION* class also contains information on the expected evaluations of the *model*, by means of attributes:

 -design_of_experiments        a set of points, in the form of a *DISCRETE_SUPPORT*, that gives the evaluations that the reduction method will **all** expect to be done 
 -training_set                 a set of points, in the form of a *DISCRETE_SUPPORT*, defining all **possible** points for the reduction method at which to evaluate the model.
                               Particularly useful for RB methods, most of the times the high-dimentional model will only be evaluated on a few points in the end

.. todo::
    As mentioned in case_data_, *VARIABLE_PARAMETER* should support not only real values, but also series and discrete supports.


This describes the *input* of the model. As for the published *outputs*, there are qualified by an **OUTPUT_DESCRIPTION** object. This object has attributes:

 -returned_type                       among the three types defined in types_of_result_: "QUANTITY_OF_INTEREST", "FIELD" or "VECTOR_OF_UNKNOWNS"
 -structure_of_returned_obj           the structure of the returned object. Depending on the *returned_type*, should be an instance of *QUANTITY_OF_INTEREST_STRUCTURE*,
                                      *FIELD_STRUCTURE* or *VECTOR_OF_UNKNOWNS_STRUCTURE*
 -output_name                         an identifier for the output
 -ref_insertion_jdd                   (optional) potential identifier in the main instruction file

As the high-dimensional model is evaluated, it produces a collection of solutions **COLLECTION_SOLUTIONS_CAS** that aggregates instances of **INDEXED_SOLUTION**. As indexed solution is a solution corresponding to an expected *OUTPUT_DESCRIPTION* for the model (through *description* attribute), that is indexed by a point in the *domain of definition*, through *indexation* attribute. These *indexed solutions* are the type of data used for the snapshots in snapshot methods.

The **INDEXATION** object gives:

 -indexation_support                  reference to the indexation support
 -parameters_value                    a point in the definition domain
 -ordinal_number                      or alternatively, for indexing empirical modes (they do not correspond to a particular value of parameters), the ordinal number of the modes
                                      (1 being higher energy mode)

.. _offline_treatments:

Offline treatments
------------------

In the previous part, we have seen all structures related to the high-dimensional simulation - even if we'll see next that structures with reduced dimension rely on them too. This data serves as input to the *offline* procedures, that is to say all procedures necessary to build a reduced-order model from & high-dimentional one and its existing solutions.

Internal solving procedures and standard functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the data model in its current state, the high-dimensional problem is solved by an external solver. As for the reduced model, for a maximal genericity the resolution code of the associated equations (ODEs, more often) will often be included in the Mordicus library: these approaches are called *non-intrusive*, and particularly useful when there is limited or no possible interaction with the external solver (e.g. commercial software). Moreover, a functional requirement of Mordicus is to support exporting the reduced-order model to standard formats (PXDMF, FMI...).

So besides the *EXTERNAL_SOLVING_PROCEDURE*, we introduce an *INTERNAL_SOLVING_PROCEDURE*, each of which is derived from an abstract **SOLVING_PROCEDURE**, see :numref:`v0_zoom5`.

.. _v0_zoom5:
.. figure:: images/v0_zoom5.pdf

   Offline treatments: zoom on custom procedures and functions


Conceptually, a *solving procedure* is a program that is able to evaluate a model - **reduced-order** or **full-order** - at a point of the parametric space. For now, in this *domain model*, *full-order* models are evaluated by *external procedures* and *reduced-order* models are by internal procedures. This is a restriction to be lifted in the future.

.. todo::
    Include in the *domain model* the case when the reduced resolution procedure calls an external solver (intrusive), still very useful in some cases

In practice, when the "model reducing user" will need to include a new kind of resolution in Mordicus (e.g. add a reduced resolution of thermal transient problems), he will have to create a new *RESOLUTION_PROCEDURE*. A *RESOLUTION_PROCEDURE* is the top-level "function" object of Mordicus datamodel. It's the only one that can be created by:

    * an end user or a module developer (for *EXTERNAL_SOLVING_PROCEDURE*)

    * a module developer (for *INTERNAL_SOLVING_PROCEDURE*)
 
So an **INTERNAL_SOLVING_PROCEDURE** is the top-level "custom function" object (functions not developed as a member of an existing Mordicus class). It deserves a peculiar treatment, with additional context and constrains because:

    * it should have a form that makes conversion to external formats (PXDMF, FMI...) easy

    * it should have enough information to be archived in a shared catalog of reduced-order models

    * there is many ODE's resolution procedures, of various techniques, and its not reasonable to ask the developer to do it by subclassing

    * developing a new solving procedure is expected to be, by far, the most frequent kind of development of module developers. It deserves a specific frame.

So that it can be found and called straight from its name, its implementation has to follow Mordicus guidelines (yet to be written). For instance, some demands to the module developer would read::

    Call it Internal_Procedure_NAME, implement in C++ and declare as extern "C" in a separate file Internal_Procedure_NAME.hpp
    Put source files in $MORDICUS_SOURCE_ROOT_DIR/src/internal_procedures
    Declare new procedure in the registry in $MORDICUS_SOURCE_ROOT_DIR/src/conf/registry.cfg

In addition to these coding principles and conventions, an *INTERNAL_SOLVING_PROCEDURE* declares its *interface*: its input arguments types should be chosen among acknowledged *offline* data structures. These are all types of *resolution data*, i.e. *offline* pre-computed data that is essential for the reduced-order model to run. For the reduction methods identified thus far in the hackathons, the comprehensive list is: *MATRIX*, *VECTOR_OF_UNKNOWN*, *REDUCED_DOMAIN*, *OPERATOR_DECOMPOSITION*, *COLLECTION_SOLUTION_CAS*, *STANDARD_FUNCTION_IMPLEMENTATION* (we'll come back to the latter case).

The attributes of the abstract *SOLVING_PROCEDURE* are:

 -procedure_reference            a identifier for the *procedure*, unique in the installation of Mordicus
 -nb_arguments                   the number of arguments of the procedure
 -resolution_data_type_in        the types of input arguments. By default, only the standard type and *File* type are supported
                                 However, in the *internal* case, additional data types are supported for input:
                                 *MATRIX*, *VECTOR_OF_UNKNOWN*, *REDUCED_DOMAIN*, *OPERATOR_DECOMPOSITION*, *COLLECTION_SOLUTION_CAS*, *STANDARD_FUNCTION_IMPLEMENTATION*

.. todo::
    Expand on the rules to implement internal procedures and conventions to reference them in the Mordicus installation.

In fact, ODE's resolution (possibly resulting from a disretization of PDE) is not the only *goal* we may have when writing a *SOLVING_PROCEDURE*. The other *goal* would be the computation of high-dimentional useful data to the reduction procedure (a mass matrix, for instance).

.. todo::
    Add *goal* attribute, with possible values "reduced-order model resolution" or "computing related data"

The *INTERNAL_SOLVING_PROCEDURE* owns attributes:

 -description_ode_pde               indicative attribute, describes the kind of ODE/PDE being solved, for easy indexing in a catalog
 -description_kind_of_problem       indicative attribute, describes the kind of physical problem being solved

.. note::
    In the current *domain model*, a frozen interface is not prescribed per goal. Doing so would require, for instance, for all reduced-order model resolution procedures to have interface ``SOLUTION_REDUITE* = Internal_Procedure_NAME(CAS_REDUIT_A_RESOUDRE*)``. We chose not to impose that because we believe it is not the module developer's responsability to extract the *offline* data from CAS_REDUIT_A_RESOUDRE, before running through the ODE's resolution. It is a standard operation Mordicus kernel should be in charge of.


The global registry of an installation of Mordicus registers two kinds of objects *SOLVING_PROCEDURE* and **STANDARD_FUNCTION_IMPLEMENTATION**. The *STANDARD_FUNCTION_IMPLEMENTATION* is the lower-level "custom function" object of Mordicus data model. By "custom function", we still mean a function that is not developed as a member of an existing class. *STANDARD_FUNCTION_IMPLEMENTATION* are meant for internal use, to fill in blanks in a higher level functions, for instance existing reduction methods or resolution procedure. Therefore, the developer has more freedom than with *INTERNAL_SOLVING_PROCEDURE* :

   * *STANDARD_FUNCTION_IMPLEMENTATION* have free interface among the data type of Mordicus, while *INTERNAL_SOLVING_PROCEDURE* has only a limited number of compatible data types;

   * *STANDARD_FUNCTION_IMPLEMENTATION* are subjected to lighter developement guidelines and conventions, and may be provided by the user during execution while *INTERNAL_SOLVING_PROCEDURE* should be loaded at runtime

For instance, some demands to the user could read::
    Be implemented in C++ and compiled separately, the file path being declared to Mordicus registry with a specific Mordicus instruction
    Abide by the interface of one of the "blank" operations known to mordicus registry
 
    We do not (yet) say how *STANDARD_FUNCTION_IMPLEMENTATION* and *INTERNAL_SOLVING_PROCEDURE* will be loaded or unloaded at runtime or even during execution (for the latter). But there are standard ways to do it even in compiled languages as C++, see e.g. here_.

.. _here: https://theopnv.com/dynamic-loading/

The *STANDARD_FUNCTION_IMPLEMENTATION* owns the following attributes:

 -implementor_id           an identifier for the registry, identifying this implementation among those sharing the same declaration 
 -implementor_file         the file implementing the function
 -expression               or a literal expression for the function (in simple cases)
 -implementor_language     the programming language used (C++ or python)

In order to verify that the provided implementations match the known blanks, calling and called functions should compare their interfaces. This is achieved by means of a **STANDARD_FUNCTION_DECLARATION** object, included in every implementation. It owns attributes:

 -func_name         function name, serves for Mordicus registry to generate the interface
 -input_types       types of input arguments, among all standard and Mordicus types
 -output_types      types of output arguments, among all standard and Mordicus types
 -namespace         the Mordicus namespace (package / class) the function should be put to

In the case of a calling *INTERNAL_RESOLUTION_PROCEDURES*, the expected prototypes of their *STANDARD_FUNCTION_IMPLEMENTATION* arguments is given by the *prototype_of_called_functions* attribute. Member functions of Mordicus classes, when declaring a "blank to be filled by a custom function", should provide the expected prototype hat goes along.

.. _compression:

Compression of data and compression of operators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A reduction procedure is often made of two steps, see :numref:`v0_zoom6`:

   * a *data compression* phase, in which one or several *reduced-order bases* are generated,

   * an *operator compression* phase, which relies on these bases to build reduced-order *resolution data*, to be employed in a reduced-order resolution procedure

.. _v0_zoom6:
.. figure:: images/v0_zoom6.pdf

    Offline treatments: zoom on the reduction methods

A **COMPRESSION_OF_DATA** procedure uses high-dimensional solutions (snapshots) to build a few space functions, making up a *reduced order basis* (*BASE_ORDRE_REDUIT*), defining a smaller subspace where to look for the solution. Let :math:`Q \in \mathbb{R}^{N \times n_s}` be the snapshot matrix, with :math:`n_s` the number of snapshots. The autocorrelation matrix can be built as :math:`Q^T M Q`, with :math:`M` the matrix of the scalar product deemed relevant to the problem, or as :math:`Q Q^T` (method of snapshots).

Possible procedure parameters are:

 -method                     among the available algorithms available for this in the install (kernel+modules) of Mordicus
 -has_fixed_basis_size       True if the user wants to build fixed-size bases
 -fixed_basis_size           if so, the number of vectors to generate in the basis
 -scalar_product_matrix      the matrix of the scalar product to use to generate the covariance matrix

Two popular families of methods are the **METHOD_POD** and **RB_METHOD**. The first has procedure parameters:

 -is_snapshot_mathod         True if the snapshot method is used
 -SVD_variant                variant of the singular value decomposition algorithm used (full SVD, thin SVD...)
 -SVD_tolerance              the relative tolerance at which SVD should be truncated (if not *has_fixed_basis_size*)

The latter encompasses greedy selection / reorthogonalization method to build a reduce basis. An argument is the relative tolerance above which the current element should be selected to enrich the basis.

While the mechanisms of *COMPRESSION_OF_DATA* are somewhat independent of the kind of problem (they mostly rely on the correlation between computed solutions), the **COMPRESSION_OF_OPERATORS** methods are much more diverse and dependent of the features of the problem.

To be as common as possible, they take as inputs:

   * a *reduced order basis*,

   * high-dimensional resolution data, the size or complexity of which shall be reduced after they have been applied.

The **RESOLUTION_DATA_OBJECT** terminology encompasses all possible data thus taken as an input. It has a *type* attribute, to be chosen (for now) among "MATRIX", "VECTOR_OF_UNKNOWNS", "DECOMPOSITION_OF_OPERATORS" or "COLLECTION_SOLUTION_CAS". In the latter case, we refer to additional pre-computed results (dual fields, typically).

The *COMPRESSION_OF_OPERATORS* returns an object with a type listed by the **REDUCED_RESOLUTION_DATA_OBJECT**: "DOMAINE_REDUIT", "SOLUTION_REDUITE_CAS" (e.g. initial condition in reduced coordinates), "BASE_ORDRE_REDUIT" (additional basis necessary to the online phase, e.g. decomposition of a non-linear term by EIM) and the 3 types listed above.

These choices stem from the analysis of input and return types for the indentified *operator compression* methods thus far, summarized in the following table:

=====================================  ======================================================  =========================================
Method                                 Types of input resolution data                          Types of output resolution data
=====================================  ======================================================  =========================================
EIM (Empirical Interpolation Method)   COLLECTION_SOLUTION_CAS, VECTOR_OF_UNKNOWNS             DECOMPOSITION_OF_OPERATORS
EQM (Empirical Quadrature Method)      COLLECTION_SOLUTION_CAS                                 REDUCED_DOMAIN
PROJECTION                             MATRIX, VECTOR_OF_UNKNOWNS (full size)                  MATRIX, VECTOR_OF_UNKNOWNS (reduced size)
HYPER_REDUCTION                        COLLECTION_SOLUTION_CAS                                 REDUCED_DOMAIN
ECSW                                   COLLECTION_SOLUTION_CAS                                 REDUCED_DOMAIN, VECTOR_OF_UNKNOWNS
=====================================  ======================================================  =========================================

Decomposition of operators
^^^^^^^^^^^^^^^^^^^^^^^^^^

Among those types, the **DECOMPOSITION_OF_OPERATORS** data type deserves some attention, see :numref:`v0_zoom5`. It describes an operator expansion that splits variables, as:

.. math::

   A(x, \mu) \approx A_1 (x) f_1 (\mu) + A_2 (x) f_2 (\mu) + ... + A_n (x) f_n (\mu)`

Of course affine decomposition of the operators falls into that case. Notably, this kind of data structure is produced by an EIM. 

It consists of an ordered list of:
   * first, *resolution_data*, representing the :math:`A_i` terms in the expansion
    
   * and *functions of parameter*, representing the :math:`f_i (\mu)` terms in the expansion
     
A **FUNCTION_OF_PARAMETER** is a means to compute :math:`f_i (\mu)` as a subclass of *STANDARD_FUNCTION_INMPLEMENTATION* where all functions arguments are parameters idenfified by their names.

It is worth pointing that *COMPRESSION_OF_OPERATORS*, as well as *DECOMPOSITION_OF_OPERATORS*, may be provided with *means* to build the *resolution data* (instead of *resolution data* itself), with possible invokation of FEM or FV asemblers. In such cases, a *RESOLUTION_PROCEDURE* is given as argument, as the *build_HD_resolution_data* attribute of *COMPRESSION_OF_OPERATORS* shows.

.. todo::
    Enrich the datamodel to allow such feature for *DECOMPOSITION_OF_OPERATORS* as well. The expected return type (among *resolution data*) is also to be added in the data model.

Online treatments
-----------------

Once the compression phases of offline_treatments_ are achieved, the *offline* part of Mordicus should act as a "generator of reduced case". In other words, it should put together all useful data to the online phase, in a formalized data structure **CAS_REDUIT_A_RESOUDRE**.

Functional requirement on *CAS_REDUIT_A_RESOUDRE*: it should be self-contained, in order to be transfered and deployed on another architecture than Mordicus. In concrete terms, the *CAS_REDUIT_A_RESOUDRE* should have access to all necessary information for the completion of the *online* phase. It's somehow the "root" object of the *online* part of the *domain model*.

The data model for the *online* part has been designed according to the following principles:

    * as far as possible, data takes the same arrangement as the corresponding high-dimensional data. This mirroring structure has several advantages:

        - clarify the meaning of the objects and the reading of the data model,

        - enable a natural reconstruction of full-field solutions from their representation in reduced coordinates,

        - easy implementation of procedures equally applicable to full-size and reduced data

    * the *online* / *offline* distinction of the operations is made in terms of their complexity: an operation is prone to online treatment if the original size :math:`N` of the case does **not** appear in its complexity. As for the distinction on the data, a piece of data is said to belong to the *online* part if :math:`N` does not appear in its size. Note that this excludes the reduced-order basis. Data not fulfilling this condition should be avoided in *CAS_REDUIT_A_RESOUDRE*, however this is not always possible especially if autonomous reconstruction of full fields is desired.

.. todo::
    Move *BASE_ORDRE_REDUIT* on the *offline* side ?

The online data structures are summarized on :numref:`v0_zoom7`

.. _v0_zoom7:
.. figure:: images/v0_zoom7.pdf

    Zoom on the online treatments

Links of the reduced case with the resolution part
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This information is made of the reduced solver *REDUCED_RESOLUTION_PROCEDURE*, accompanied by the case-specific *REDUCED_RESOLUTION_DATA* that complement it (see compression_), both of which are gathered by the **REDUCED_SOLVER_DATASET** object, through its attributes, itself referenced by *CAS_REDUIT_A_RESOUDRE*. 

In accordance with the above, it can be easily seen that data is thus arranged as *SOLVER_DATASET* was around *INTERNAL_REDUCTION_PROCEDURE*: *REDUCED_SOLVER_DATASET* inherits *INTERNAL_SOLVER_DATASET* in order to include support for base *RESOLUTION_DATA_OBJECTS* (which the have reduced size) and *STANDARD_FUNCTION_IMPLEMENTATION*. 

.. note::
    For now, *REDUCED_RESOLUTION_DATA* does not inherit *RESOLUTION_DATA_OBJECT* so that types only used in the reduced case are clearly put apart.

Links of the reduced case with the input/output definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The mechanism for qualifying the user inputs and outputs of the reduced-order model (*CAS_REDUIT_A_RESOUDRE*) take a cue on the full-size counterpart (*CASE_DATA*), see io_indexing_. Indeed, variable input parameters are specified by *VARIABLE_PARAMETER* objects, referencing their *domain of definition* through an *INDEXING_SUPPORT*. Fixed parameters are now hidden, or available for consultation only. Outputs are qualified by a reference to *OUTPUT_DESCRIPTION* objects.

The indexing mechanism for classifying evaluations of the reduced-order model follow the very same rules as in io_indexing_: a *CAS_REDUIT_A_RESOUDRE* contains its evaluation through a **SOLUTION_REDUITE_CAS**, a class that inherits *INDEXED_SOLUTION* and its indexing mechanism.

.. note::
    For now, *CAS_REDUIT_A_RESOUDRE* does not inherit *CASE_DATA*, so that it can "hide" or "filter" information from the full size model. To be discussed. Add at least a possible reference to the original case?
   
    Attributes *case_reference* and *case_documentation* are nevertheless kept for obvious indicative purposes.

The reduced basis and representation in reduced coordinates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So that the solution can be easily reconstructed, *SOLUTION_REDUITE_CAS* is based on restricted structures (*RESTRICTION_FIELD_STRUCTURE* and *RESTRICTION_UNKNOWNS_STRUCTURE*), the underlying columns being nothing but the vectors of the reduced basis, see types_of_result_. Two cases can be indentified here:

   * the case when reconstruction has to be autonomous, the whole *field structure* and *discrete support* are then embarked when the reduced-order model is exported;

   * the case when performance is preferred. Then, when exported, the reduced-order model only keeps meta data about the *field structure* object (including a checksum), but does not embark futher information. Reconstruction of a field is then no longer possible, except if that structure is provided by some other means on the deployement side. Metadata then ensures some verifications.

The reduced basis is represented by **BASE_ORDRE_REDUIT** object that aggregates *VECTEUR_BASE_ORDRE_REDUIT* and owns qualifying attributes:

  -nb_dofs                   the size :math:`N` of each vector in the basis
  -dof_weights               (optional) in the case of a diagonal scalar product matrix,
                             the corresponding coefficient of each dof
  -is_orthogonal             True if the basis is orthogonal
  -role                      role of the basis in the *reduction of operators* mechanism
                             among "Galerkin", "Petrov-Galerkin left", "Petrov-Galerkin right"...
  -singular_values           the ordered list of singular values for each empirical mode

.. note::
    *BASE_ORDRE_REDUIT* does not inherit *COLLECTION_SOLUTION_CAS* for now, for clarity and because the attributes they own are quite different. Inheritance happens between the objects they aggregate

The **VECTEUR_BASE_ORDRE_REDUIT** object basically inherits the *INDEXED_SOLUTION* case, the indexation happening by *ordinal_number* attribute: the first (higher singular value) mode is indexed 1, the next 2 and so on.


The reduced domain object
^^^^^^^^^^^^^^^^^^^^^^^^^

Many reduction methods (Hyper-reduction, EQM, ECSW...) appeal to a selection of a few entities in the original *DISCRETE_SUPPORT* to compute relevant approximations of the integrals and operators. Therefore, a **REDUCED_DOMAIN** class is introduced to represent this notion.

The *REDUCED_DOMAIN* references its original *DISCRETE_SUPPORT*. However, this "filter" has itself to be a self-contained *DISCRETE_SUPPORT*, because it should be possible to export the reduced-order model without embarking the whole original *support* for performance purposes. In this case, only metadata about the original support are kept when exporting.

According to the method, the *REDUCED_DOMAIN* can be a subdomain with the same kind of entities as the original support: in other words, it's a true FEM mesh, as in the *HYPER_REDUCTION* method for instance. In other cases, it is merely a cloud of *POINTS* defining a global quadrature scheme, the associated weights being then borne by a *quadrature_weights* attributes.


