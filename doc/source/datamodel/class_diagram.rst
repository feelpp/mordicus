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
.. figure:: images/v1-zoom6.pdf

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
.. figure:: images/v1-zoom7.pdf

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

What piece of data each use case employs
========================================

A.01 - Usage d'un mod??le r??duit pour r??aliser un plan d'exp??rience
------------------------------------------------------------------

*Pour une ??valuation du mod??le r??duit*

On utilise l'objet **CAS_REDUIT_A_RESOUDRE**, qui par d??finition doit contenir l'ensemble des donn??es et instructions n??cessaires pour ??valuer le mod??le r??duit en un point. Le syst??me commence par remplacer la configuration variable par la valeur fournie par l'utilisateur ?? l'aide du nom de param??tre, en substituant la *ref_insertion_jdd* par la valeur fournie par l'utilisateur. Le syst??me ex??cute les instructions du **REDUCED_SOLVER_DATASET** en faisant appel ?? une **INTERNAL_SOLVING_PROCEDURE**. Ces instructions utilisent les op??rateurs et donn??es de complexit?? r??duites qui ont ??t?? g??n??r??es *offline* et sont connues du **REDUCED_SOLVER_DATASET**. Concr??tement, il peut s'agir d'objets de nature diverses: matrices (**MATRIX**) et vecteur (**VECTOR_OF_UNKNOWS**) de complexit?? r??duite dans le cas non intrusif, pour lequel la r??solution temporelle a ??t?? recod??e pour le mod??le r??duit, et approximation des op??rateurs non-lin??aires par d??composition affine ou autres s??ries de fonctions **DECOMPOSITION_OF_OPERATORS**. Dans d'autres cas, les op??rateurs sont recalcul??s/assembl??s ?? l'int??rieur de la **INTERNAL_SOVING_PROCEDURE**, auquel cas ils ne sont pas "vus" par le mod??le de donn??es de Mordicus. Dans ce cas, les donn??es dont a besoin la proc??dure de r??solution sont des quantit??s moins directement li??es ?? la r??solution alg??brique ms permettant de calculer le syst??me ?? r??soudre, comme un domaine de calcul r??duit ou un sch??ma de quadrature par exemple.

*Pour l"utilisation en plan d'exp??rience*

L'utilisateur donne le plan d'exp??rience via un **DISCRETE_SUPPORT** qui doit ??tre en coh??rence avec le **SUPPORT_INDEXATION** fourni dans le mod??le r??duit. Les ??valuations du mod??le r??duit peuvent ??tre appel??es en distribu?? (dans des threads diff??rents). Les solutions, de type **SOLUTION_REDUITE_CAS** sont ajout??es ?? l'objet **CAS_REDUIT_A_RESOUDRE** du processus ma??tre (celui de l'application Mordicus qui a lanc?? les calculs distribu??s) au fur et ?? mesure qu'elles arrivent. 

A.02 - Utilisation d'un mod??le r??duit avec des mesures in-situ (en laboratoire, sur site de production...)
----------------------------------------------------------------------------------------------------------

L'id??e est de pouvoir appeler l'objet **CAS_REDUIT_A_RESOUDRE** dans un environnement tourn?? vers l'exp??rimental ou la mesure. Par exemple Labview, Simulink... Pour cela, un export du mod??le r??duit comme FMU dans le standard FMI permettrait-il d'interagir avec ces syst??mes ? Liste des logiciels support??s par le FMI ici https://fmi-standard.org/tools/

Cela impliquerait:

   * que Mordicus sache exporter un **CAS_REDUIT_A_RESOUDRE** au format FMU, ou autre format cible du syst??me de contr??le commande, ?? certaines conditions (par exemple que l'int??gralit?? des instructions d'??valuation du mod??les soient ??crites en langage C);

   * que le syst??me de contr??le/commande et acquisition de donn??es sache fournir ?? ce FMU les signaux exp??rimentaux sous la forme attendue par le FMU, qui est celle de **QUANTITY_OF_INTEREST** de Mordicus.

.. todo::

   Demander aux partenaires utilisateurs du use case quels sont leurs logiciels de test, contr??le / commande pour les syst??mes concern??s

Par "interaction avec des mesures", on entend:

   #. donner au mod??le r??duit un signal d'entr??e provenant de mesures (dans le cas o?? la variabilit?? est "non param??trique" ou "mixte"), et l'appeler dans l'environnement logiciel d??di??. Ceci inclut le cas o?? le "mod??le r??duit" est en fait une proc??dure d'assimilation de donn??es et les mod??les r??duits de syst??mes d'??tat. Le mod??le r??duit est alors une brique de la cha??ne de contr??le commande.

   #. comparer une quantit?? d'int??r??t (**QUANTITY_OF_INTEREST**) calcul??e en sortie d'un mod??le r??duit avec la m??me quantit?? mesur??e exp??rimentalement, et calculer des indicateurs d'??cart sur cette comparaison.

.. todo::

    Adapter le mod??le de donn??es pour prendre en compte le cas o?? le "mod??le r??duit" est en fait une proc??dure d'assimilation de donn??es. Pour inclure le cas o?? la variabilit?? d'entr??e est non param??trique, il faut que *parameter_value* d'indexation puisse ??tre une valeur de type **QUANTITY_OF_INTEREST**. Il faut revoir aussi le sens de l'objet interm??diaire **SUPPORT_INDEXATION**


A.03 - Utilisation d'un mod??le r??duit comme brique d'un "clone digital" ou d'un code syst??me
--------------------------------------------------------------------------------------------

Il s'agit de pouvoir appeler un objet **CAS_REDUIT_A_RESOUDRE** dans un logiciel de mod??lisation de syst??mes complexes, par exemple Modelica, EMTP, Simulink... La discussion pr??c??dente sur l'environnement tourn?? vers l'exp??rimental s'applique.


A.04 - Reconstruire un champ complet ?? partir des sorties d'un mod??le r??duit
----------------------------------------------------------------------------

On part d'une **SOLUTION_REDUITE_CAS** de type champ (**FIELD**) qui est une repr??sentation "compress??e" d'un champ. Suivant les cas et les m??thodes, il peut s'agir:

   * des coefficients de la solution dans une base r??duite (**BASE_ORDRE_REDUIT**)
    
   * de la valeur du champ en certains points (noeuds ou points de Gauss), ou de certains moments du champ (int??grale fois une fonction spatiale)

On souhaite transformer cet information en un champ **INDEXED_SOLUTION** (avec un attribut *reconstructed*) sur le maillage complet original, afin de visualiser une information qui a un sens physique clair. Pour reconstruire ce champ complet, on va respectivement:

   * appliquer la combinaison des coefficients et modes de la base (combinaison lin??aire par d??faut), sinon la d??composition est donn??e par un objet de type **DECOMPOSITION_OF_OPERATORS**

   * appliquer une m??thode de type "moindre carr??es" sur une base de fonctions donn??es (Gappy POD), laquelle est donn??e par un objet **BASE_ORDRE_REDUIT**

Dans le second cas, il est n??cessaire de disposer de la localisation des valeurs donn??es, ou du moins de la fa??on d'extraire cette valeur pour chaque mode (afin de calculer les op??rateurs de la Gappy POD). Cette information est donn??e par un objet **RESTRICTION** donnant dans un seul **FIELD** la valeur de cette fonction spatiale. On doit ??galement dire si l'extraction se fait par un produit scalaire :math:`L^2 (\Omega)` (ce qui sera le cas pour les moments) ou un produit scalaire alg??brique :math:`l^2` (ce qui sera le cas pour les extractions de valeurs ponctuelles).

.. todo::

   Reporter cette derni??re information dans le mod??le de donn??es

A.05 - Permettre la visualisation HPC des r??sultats du mod??le r??duit
--------------------------------------------------------------------

Ce cas se pr??sente, particuli??rement en CFD, lorsque le champ complet du cas A.04 est trop volumineux pour ??tre visualis?? sur un seul noeud (une seule barrette m??moire, bon je ne ma??trise ??s trop tout ces concepts).

On dispose alors d'un outil de visualisation permettant de faire les traitements de visualisation en parall??le. Ceci est hors resposabilit?? de Mordicus.

En revanche, dans cette perspective, Mordicus doit ??tre capable de fournir un champ complet par sous-domaine (on parle de parall??lisme MPI). Il faudra discuter des donn??es connues de chaque processeur dans ce cas:

   * soit chaque processeur a une copie de l'ensemble des donn??es, le **DISCRETE_SUPPORT** repr??sentant uniquement le sous-domaine, les **FIELD**, les **VECTEUR_BASE_ORDRE_REDUIT** de type FIELD devant ??tre consid??r??s comme la restriction au sous-domaine consid??r??. Dans cette approche, tout est local, il n'y a aucune information de correspondance locale -> globale sur la num??rotation. Ce n'est pas g??nant si on cherche uniquement ?? calculer des int??grales en parall??le par exemple, c'est donc l'approche suivie dans la maquette actuelle. Cela devient g??nant si on veut imposer des traitements inter-domaines qui on besoin de cette correspondance, par exemple si on souhaite imposer des relations entre deux inconnues de deux sous-domaines diff??rents. Pour ce use case, cette approche suffit donc. Elle a l'avantage de ne n??cessiter aucun changement au mod??le de donn??es actuel.

   * soit, seul un processus 0 poss??de l'ensemble du mod??le de donn??es, y compris un maillage en num??rotation globale avec des informations de correspondance pour chacun des sous-domaines. Les autres processeurs voient uniquement le maillage du sous-domaine, les **FIELD** et les **VECTEUR_BASE_ORDRE_REDUIT** sur le sous-domaine. Ce processeur 0 est capable de reconstruire des champs complets en num??rotation globale. N??anmoins, cela n??cessiterait de modifier le mod??le de donn??es pour faire appara??tre ces correspondances de num??rotation.

A.06 - Exporter (s??rialiser) un mod??le r??duit au format d'??change
-----------------------------------------------------------------

Il s'agit d'??crire sur disque dans un format p??renne l'objet **CAS_REDUIT_A_RESOUDRE** et toutes ses d??pendances n??cessaires pour pouvoir ??valuer une nouvelle configuration (une nouvelle valeur de param??tre) du mod??le r??duit. 

Ce qui nous donnerait les objets suivants ?? sauvegarder:

.. todo::

   Sous-mod??le de donn??es des quantit??s ?? sauvegarder

Parmi ces quantit??s, certaines sont strictement n??cessaire pour appeler le mod??le r??duit et sont de complexit?? minimales, et d'autres (comme la **BASE_ORDRE_REDUIT**) sont des informations de contexte plus volumineuses utiles pour reconstruire des champs complets (ms pas strictement n??cessaires si tel n'est pas le but).

A discuter: la proc??dure interne de r??solution capable d'ex??cuter les instructions peut ??tre:

    * embarqu??e dans la sauvegarde, ce qui ne para??t r??aliste qu'?? condition que cette proc??dure soit ??crite sous une certaine forme et puisse dire sous une certaine forme quelles sont ses d??pendances. Par exemple: script python autoportant avec un fichier requirements.txt de pip disant quelles sont les autres modules python n??cessaire pour ex??cuter ce script. Idem par exemple pour un script shell avec les paquets Debian.

    * pr??-enregistr??e dans une installation de Mordicus. On imagine que chaque installation de Mordicus a un "registre" o?? on peut ajouter des proc??dures de r??solution. On appelera alors la proc??dure du registre. Au moment o?? le d??veloppeur (utilisateur C) termine une nouvelle m??thode de r??solution interne, il peut l'int??grer par d??faut ?? la version de Mordicus de son entit?? (via les modules adapt??s), et les futurs utilisateurs A qui installeront Mordicus y auront acc??s. Il faut aussi que ce d??veloppeur puisse contacter les utilisateurs A qui ont une ancienne version de Mordicus pour qu'ils ajoutent cette nouvelle m??thode au registre.

A.07 - Importer (d??s??rialiser) un mod??le r??duit au format d'??change
-------------------------------------------------------------------

L'op??ration inverse de ce qui pr??c??de.

A.08 - Archiver un mod??le r??duit ou une liste de mod??les r??duits
----------------------------------------------------------------

Ce use case utilise A.06 et A.07 et utilise par cons??quent les m??mes donn??es.

De plus, il implique un certains nombre d'informations:

   * pour indentifier de fa??on non ambig??e le mod??le r??duit ?? r??cup??rer,

   * pour le retrouver.

Pour identifier, c'est l'attribut *case_reference* de **CAS_REDUIT_A_RESOUDRE** qui s'en occupe. Doit-on s??parer en *case_reference* (l'objet d'??tude, le cas m??tier, par ex "r??duction du calcul thermique du clapet X") et *case_version* (la version de l'??tude qui peut avoir plusieurs variantes, par exemple s'il a ??t?? trait?? par diff??rentes m??thodes de r??duction "traitement par POD classique"), la combinaison des deux devant ??tre unique parmi les objets archiv??s.

Pour le retrouver, il est n??cessaire d'avoir des informations "documentaires" sur le cas m??tier: champ de description libre *case_documentation*, mot-cl??s (?? ajouter) 

A.09 - Contr??ler qu'un mod??le r??duit conserve certaines propri??t??s math??matiques du mod??le haute fid??lit?? sur un sous-domaine
-----------------------------------------------------------------------------------------------------------------------------

Dans ce cas, veut v??rifier que certaines propri??t??s du mod??le haute fid??lit?? sont respect??es. Par exemple: stabilit?? d'un syst??me lin??aire invariant (tous les p??les sont ?? partie r??elle n??gative), stabilit?? :math:`L^2` ou :math:`L^\infty` d'un sch??ma en temps, stabilit?? inf-sup dans la discr??tisation d'un probl??me de point-selle (typiquement Navier-Stokes incompressible), positivit?? des solutions et n??gativit?? des multiplicateurs d'une in??galit?? variationnelle, conservation d'une ??nergie totale...

On peut classer en deux cas:

   * le respect de cette propri??t?? est ??valuable par une fonction de post-traitement sur les solutions et/ou les op??rateurs du mod??le r??duit. Par exemple: on calcule les p??les de la fonction de transfert r??duite, on v??rifie qu'une temp??rature se trouve entre des bornes min et max... Cela implique bien s??r que l'appel de cette fonction a un co??t raisonnable. Cette fonction est fournie par l'utilisateur C avec le mod??le r??duit

   * le respect de cette propri??t?? n'est pas ??valuable par une fonction de post-traitement. Par exemple, juger de la stabilit?? inf-sup d'une discr??tisation implique au moins deux maillages diff??rents et des calculs de valeurs propres avec un co??t ??lev??, et m??me avec cette information on ne peut pas conclure de fa??on univoque. Dans ce cas, c'est l'expertise de l'utilisateur C ?? la vue des solutions qui fournira une r??ponse (par exemple oscillation non-physique de la solution).

On parle ici uniquement du cas 1, le 2 est trait?? via A.05 "visualiser un champ complet".

La fonction de post-traitement est donn??e via un **QUALITY_INDICATOR** de type *mathematical_property* (?? ajouter). Elle contient un lien vers le **REDUCED_POSTPROCESSING_DATASET**, qui lui-m??me contient tous les op??rateurs (matrices et vecteurs, contenus dans **REDUCED_RESOLUTION_DATA**) n??cessaires pour ce calcul. En plus de ces op??rateurs, on a aussi acc??s ?? ceux de la r??solution **REDUCED_SOLVER_DATASET**, et bien entendu ?? la solution r??duite.

Les **REDUCED_POSTPROCESSING_DATASET** sont produits en m??me temps que le mod??le r??duit et sont con??us pour fonctionner ?? la suite d'une certaine m??thode de r??solution r??duite. Ces objets sont donc contenus dans **REDUCED_SOLVER_DATASET**, comme des post-traitements possibles de cette r??solution.

.. todo::

    Reporter tout ??a dans le mod??le de donn??es plut??t qu'un usage des **STANDARD_FUNCTION_IMPLEMENTATION** r??serv??es aux fonctions fournies par un utilisateur. S'il n'y a aucune partie de l'indicateur d'erreur qui ont ??t?? pr??cod??es, et donc que l'usage d'une **STANDARD_FUNCTION_IMPLEMENTATION** serait le plus direct, on peut facilement d??duire ce cas avec un *dataset* vide qui appelle la fonction. 

.. todo::
    
    Faut-il envisager des sous-types (energy conservation, mass conservation, stability of time scheme...) ?

A.10 - Couplage spatial entre un mod??le r??duit et un mod??le haute fid??lit??
--------------------------------------------------------------------------

Dans ce cas, on couple dans la r??solution un mod??le haute-fid??lit?? pour couvrir une zone d'int??r??t et un mod??le r??duit pour la majeure partie du syst??me. C'est le cas par exemple quand on fait des mod??les r??duits en m??canique des fluides avec une g??om??trie variable uniquement sur une petite partie du domaine.

A premi??re vue, cela implique de faire communiquer un **CASE_DATA** avec un **CAS_REDUIT_A_RESOUDRE** ?

Les m??thodes peuvent diff??rer sur la fa??on de faire ce couplage. On note en g??n??ral:

   * n??cessit?? de faire un calcul HF en donnant comme conditions limite un field sur un domaine plus grand (et discr??tis?? plus grossi??rement, souvent)

   * reconstruire par Gappy POD les coefficients ?? partir de valeurs dans un zoom -> couvert par le use case A.04

   * construire des solutions hybrides en prenant un champ calcul?? sur un sous-domaine et un champ reconstruit ailleurs

   * projection de Galerkin pour partie avec des modes et pour partie avec des vraies fonctions ??l??ments finis ou volumes finis.

On est dans le m??me cas que la m??thode NIRB, o?? on a besoin de calculer des solutions HF sur un autre domaine, ou une autre discr??tisation du domaine. Cet appel ne peut pas ??tre enti??rement bo??te noire, car il faut avoir certaines informations pour effectuer les traitements sur cette solution. Il faut avoir le sous-domaine de calcul, et savoir faire des produits scalaires avec les modes (pour la Gappy POD). Cela prend la forme d'un **SOLVER_DATASET** contenu dans les **REDUCED_RESOLUTION_DATA**, contenant comme *resolution_data* un **REDUCED_DOMAIN**. Pour corser le tout, celui peut ??tre donn?? comme param??tre d'entr??e du mod??le r??duit (exemple avec g??om??trie variable).

.. todo::

   Demander un exemple ?? CT, ils en avaient un


A.11 - Calculer des quantit??s physiques d'int??r??t macroscopiques, par post-traitement (par ex dur??e de vie)
-----------------------------------------------------------------------------------------------------------

Note: il faut exhiber les formes lin??aires x les vecteurs de la base pour exhiber les quantit??s int??grales lin??aires qui vont servir pour le calcul des quantit??s. Une fois qu'on les a, on applique une **STANDARD_FUNCTION_IMPLEMENTATION**, afin que **QUANTITY_OF_INTEREST_STRUCTURE** ne r??f??rence plus **RESTRICTION_FIELD_STRUCTURE** directement. 

.. todo::

    Il faut ajouter des objets **QUANTITY_OF_INTEREST_COMPUTATION** et **REDUCED_QUANTITY_OF_INTEREST_COMPUTATION** dans le mod??le de donn??es.


A.12 - Optimiser le placement des capteurs dans un syst??me
----------------------------------------------------------

Tr??s souvent, on part d'un ensemble discret (mais de grandes taille) de positions possibles pour les capteurs.

On peut distinguer deux cas:

   * celui o?? on dispose effectivement de signaux exp??rimentaux ou de synth??se pour tous ces capteurs

   * celui o?? on ne dispose pas de tels signaux.

On boucle sur les signaux en ajoutant incr??mentalement le signal le moins bien approxim??. Je ne connais pas d'exemple dans le premier cas. Dans le second, cela se fait ?? l'aide du supremizer de la constante inf-sup pour la m??thode PBDW (cf th??se Amina Benaceur) et l'approximation des snapshots par la base r??duite en cours de construction pour GEIM.

On a donc besoin:

   * de la **BASE_ORDRE_REDUIT**

   * du **RESTRICTION_FIELD_STRUCTURE** repr??sentant la localisation pour chaque capteur,

   * d'un **QUALITY_INDICATOR** de type "approximation of signal" avec une **STANDARD_FUNCTION_IMPLEMENTATION** qui connait ces deux premiers ??l??ments.


A.13 - Evaluer le mod??le r??duit en un point (cas d'usage de plus bas niveau)
----------------------------------------------------------------------------

Trait?? en A.01

A.14 - Calculer un indicateur de qualit?? a posteriori pour un appel de mod??le reduit
------------------------------------------------------------------------------------

L'usage des donn??es est identique ?? A.09: On d??finit un **QUALITY_INDICATOR** de type "a posteriori" qui va appeler un **REDUCED_POSTPROCESSING_DATASET**. L'indicateur peut n??cessiter la solution duale, la solution primale ou les deux. Dans certains cas, une proc??dure *offline* a permis d'??valuer ces indicateurs de fa??on rapide, qui sont donn??es sous forme de **REDUCED_RESOLUTION_DATA**.

B - Utilisateur connaissant le mod??le complet
=============================================

B.01 - Cr??ation d'un mod??le r??duit avec garantie de fiabilit?? sur un domaine param??trique donn??
-----------------------------------------------------------------------------------------------

Les use case de cr??ation d'un mod??le r??duit suivent le processus suivant:

    1. l'utilisateur fournit les information pour caract??riser le probl??me et sa variabilit??;

    2. l'utilisateur r??cup??re ou fait calculer par le solveur haute-fid??lit?? les op??rateurs HF qui sont des donn??es d'entr??e pour la phase d'apprentissage;

    3. l'utilisateur r??colte et caract??rise les r??sultats haute-fid??lit?? depuis des fichiers r??sultats;

    4. l'utilisateur lance la phase d'apprentissage (phase offline), en sp??cifiant *certaines options*;

    5. le syst??me effectue la phase d'aprentissage et produit les objets constituant le mod??le r??duit **CAS_REDUIT_A_RESOUDRE**.

Dans ce use case, on ne sp??cifie pas explicitement une m??thode d'apprentissage pour la phase 4. On donne en revanche un **QUALITY_INDICATOR**. N??anmoins, concr??tement toutes les m??thodes de r??duction ne sont pas applicables ?? tous les probl??mes (beaucoup sont sp??cifiques ?? un probl??me particulier, comme les m??thodes de projection de Galerkin par exemple). Il faut donc que l'utilisateur fournisse, pour son type de probl??me:

    * les m??thodes de r??duction **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS** qui sont applicables en 4;

    * une proc??dure de r??duction "ma??tre" (**REDUCTION_PROCEDURE**) qui dira comment effectuer les ??tapes 3-4 afin d'arriver ?? l'objectif fix?? sur l'indicateur de qualit??. Ces ??tapes 3-4 sont parfois effectu??es ?? l'int??rieur d'une boucle, c'est-??-dire en traitant l'aprentissage d'un r??sultat haute-fid??lit?? ?? la fois, avant de calculer le prochain. Dans ce cas, la proc??dure de r??duction "ma??tre" s'occupe aussi de l'??chantillonage des calculs HF.

On a d??j?? un premier probl??me ?? ce stade: l'utilisateur B n'est pas sens?? avoir les comp??tences pour dire quelles sont les m??thodes applicables pour son probl??me, en tout cas pas sans l'aide de l'utilisateur C. Il faudrait pour cela ajouter dans l'objet **REDUCTION_PROCEDURE** les m??thodes de r??duction des donn??es et des op??rateurs qui sont applicables, information qui serait ?? renseigner par l'utilisateur C quand il ??crit la **REDUCTION_PROCEDURE**.

.. todo::

   Ajouter dans l'objet **REDUCTION_PROCEDURE** les m??thodes de r??duction des donn??es et des op??rateurs qui sont applicables

On peut imaginer que le syst??me lance plusieurs m??thodes de r??duction en m??me temps (ce qui est co??teux), et s'arr??te d??s qu'il y en a une qui atteint la pr??cision demand??e. Pour ??viter le co??t, on peut lancer une premi??re phase d'essai avec une pr??cision tr??s l??che uniquement afin de s??lectionner la meilleure m??thode.

*Caract??risation du probl??me et de sa variabilit??*

Cette phase est d??clarative: l'utilisateur cr???? l'objet racine *CASE_DATA* avec sa documentation et une r??f??rence (voir use case A.08). Il caract??rise les sorties attendues du probl??me (les r??sultats) en remplissant des objets **OUTPUT_DESCRIPTION**. Il dit ??galement quels sont les param??tres du probl??me: ils peuvent ??tre r??els - par abus de langage on parlera de "cas param??trique" - ou non. On les renseigne via **VARIABLE_PARAMETER**, et la quantit?? physique associ??e **PHYSICAL_QUANTITY**, mis ?? part l'attribut *available_components* qui est sans objet dans ce cas.

Dans le cas param??trique, on donne le domaine param??trique **SUPPORT_INDEXATION** via des bornes sur chaque valeur, ou la r??f??rence d'une fonction prenant les param??tres en argument et retournant un bool??en d'appartenance au domaine de d??finition. Plus tard, en 3, on renseignera dans ce domaine param??trique les points o?? une solution HF doit ??tre disponible (le *design of experiment* et les points o?? une solution HF est susceptible d'??tre calcul??e (le *training set*).

On d??finit aussi des maillages **DISCRETE_SUPPORT** de r??f??rence pour la discr??tisation spatiale et temporelle. Ils serviront pour la compression des don??es.

Le contenu d??taill?? des objets n'est pas rappel?? ici car il est d??crit dans le datamodel.

.. note::

    On notera que l'**OUTPUT_DESCRIPTION** contient un objet **RESTRICTION_FIELD_STRUCTURE**, ou ??quivalent pour les sorties qui ne sont pas de type field, qui donnent la structure fixe attendue pour les r??sultats. En effet, pour pouvoir compresser les r??sultats, il faut qu'ils aient tous la m??me structure. Celle-ci dit ?? quelle *entit?? du maillage* et ?? quelle *composante de la grandeur* se rapporte chaque valeur dans le champ. Cependant, donner cette structure avant d'avoir lu le moindre r??sultat peut ??tre compliqu?? en pratique, c'est pourquoi on laisse ??galement la possibilit?? de ne la remplir qu'?? la lecture du premier r??sultat (??tape 2).

*R??cup??ration ou calcul des op??rateurs HF*

La proc??dure ?? utiliser pour produire ces op??rateurs est contenue dans un objet **PREPROCESSING_DATASET**, lequel r??f??rence le solveur ?? utiliser (**SOLVING_PROCEDURE**). En revanche, les liens de cet objet **SOLVER_DATASET** sont diff??rents du cas **REDUCED_POSTPROCESSING_DATASET**. En effet, cet objet **PREPROCESSING_DATASET** n'est pas reli?? au **SOLVER_DATASET**, car on put vouloir calculer des op??rateurs (matrice d'un produit scalaire sur un certain maillage par exemple) ind??pendamment d'un cas de calcul explicite avec le solveur. En outre, dans certains cas, on n'a pas acc??s au solveur dataset: imaginons par exemple un cas dont on r??cup??re les r??sultats sans avoit les fichiers qui les ont g??n??r??s. Si on a le maillage, on peut toujours calculer la matrice du produit scalaire par un autre outil externe.

Un objet **PREPROCESSING_DATASET** produit les **RESOLUTION_DATA_OBJECT** sp??cifique ?? une m??thode de r??duction **REDUCTION_PROCEDURE** pour un certain cas **CASE_DATA**.

Un **PREPROCESSING_DATASET** ?? une **REDUCTION_PROCEDURE**, et par cet interm??diaire ?? un **CASE_DATA**. Plusieurs m??thodes pouvant ??tre utilis??es sur un **CASE_DATA** (l'objet **CASE_DATA** est agnostique de la m??thode d'aprentissage qui sera utilis??e, il se contente de d??crire le probl??me et sa variabilit??), le lien ?? cet objet ?? lui seul ne suffit pas.

.. todo:: 

    Dans le mod??le de donn??es, mettre le lien HD_resolution_data ?? **REDUCTION_PROCEDURE** au lieu de **COMPRESSION_OF_OPERATORS** (exemple matrice d'un produit scalaire)

Une m??thodologie de r??duction est pr??vue pour fonctionner pour une classe de probl??mes (exemple "thermique lin??aire instationnaire depuis calculs Code_Aster"), avec des modification mineures en fonction du cas ??tudi?? dans cette classe (exemple "clapet A"): seul des noms de groupes d'??l??ments du maillage ou certaines options de calcul changeront. On a donc int??r??t ?? mettre en place une structure de *template* d'une proc??dure de r??duction pour une *classe de probl??me*.

Concr??tement, **REDUCTION_PROCEDURE** peut avoir ??t?? cr???? en remplissant un **REDUCTION_PROCEDURE_TEMPLATE**, lequel s'applique ?? une **CLASS_OF_PROBLEMS**.

Sur un sch??ma identique, un **PREPROCESSING_DATASET** peut avoir ??t?? cr???? depuis un **PREPROCESSING_DATASET_TEMPLATE** qui s'applique ?? une classe de probl??mes, et laisse vide certaines caract??ristiques d??pendantes du cas.

.. todo::

   A reporter dans le mod??le de donn??es

Dans ce use case, l'utilisateur B va donc adapter un **PREPROCESSING_DATASET_TEMPLATE** (qui aura ??t?? ??crit par l'utilisateur C), et lancer le calcul des **RESOLUTION_DATA_OBJECT** qui seront n??cessaires pour la proc??dure d'apprentissage.

*R??colte des r??sultats haute-fid??lit??*

En d??pendance de la proc??dure de r??duction, l'utilisateur peut disposer des r??sultats haute-fid??lit?? au d??but ou les faire calculer par le solveur (cas ...).

Typiquement, l'utilisateur aura une arborescence avec un dossier pour chaque configuration (valeur de param??tre) comme en :numref:`reading_results_folder`.

.. _reading_results_folder:
.. figure:: images/reading_results_folder.png

    Typical folder structure with input HF results, mesh and other operators

Pour chaque r??sultat, l'utilisateur va appeler un *reader* qui va transformer le r??sultats sur disque (au format du solveur qui l'a produit), en une **INDEXED_SOLUTION**. L'utilisateur fournit pour chaque configuration la valeur de param??tre, que le syst??me va transformer en objet **INDEXATION** dont il se servira pour acc??der aux diff??rentes *solutions*. L'utilisateur fournit ??galement le type de r??sultat qui est attendu pour chaque lecture, parmi **QUANTITY_OF_INTEREST**, **VECTOR_OF_UNKNOWN**, **FIELD**.

Il y a en effet des m??thodes de r??duction adapt??es ?? chacun des 3: le plus courant est sans doute **FIELD** (POD...), mais on peut faire par exemple de la reconstruction de fonction de transfert ?? partir de **QUANTITY_OF_INTEREST** (m??thode de Loewner...) ou des POD par composantes ?? partir d'un **VECTOR_OF_UNKNOWN**.

Pour que la compression de donn??es puisse marcher - et c'est une exigence commune ?? toutes les m??thodes ?? ma connaissance - il faut que tous les r??sultats du m??me type aient la m??me *structure*. Si celle-ci n'a pas ??t?? d??duite lors de la phase 1 (voir note plus haut), elle est d??duite de la premi??re lecture de r??sultat via le *reader* et v??rifi??e pour les lectures suivantes ensuite.

*Options de la phase d'apprentissage*

Pour ce use case, l'utilisateur va partir d'un *template* d'une **REDUCTION_PROCEDURE** compatible avec sa classe de probl??me **CLASS_OF_PROBLEMS**. Il adapte ce template, en se faisant aider si besoin par l'utilisateur C, les modifications ??tant en g??n??ral mineures (sinon, il s'agit d'une nouvelle classe de probl??mes).

La **REDUCTION_PROCEDURE** fait appel ?? des m??thodes de compression des donn??es et des m??thodes de compression des op??rateurs **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS**, avec certaines options (tol??rances etc.). Dans ce use case, l'utilisateur souhaite en tester plusieurs, il va donc pour chaque test dire quelle m??thodes **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS** il souhaite utiliser, parmi celles que le template autorise, et avec quelles options.

L'utilisateur B donne enfin la pr??cision d??sir??e sur la r??duction, ainsi que le **QUALITY_INDICATOR** (parmi ceux qui se r??f??rent ?? la **REDUCTION_PROCEDURE**) qui sera utilis?? pour l'??valuer. Il faut que la proc??dure de r??duction se base sur ces ??valuations pour enrichir l'approximation (par exemple m??thodes de bases r??duites).

.. todo::

   Ajouter ?? l'objet **REDUCTION_PROCEDURE**:

      - la pr??cision d??sir??e sur la r??duction

      - les m??thodes **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS** support??es.

*Ex??cution de la phase d'apprentissage*

On peut distinguer les m??thodes "en bloc" des m??thodes incr??mentales.

La **REDUCTION_PROCEDURE** va typiquement appliquer une premi??re phase de compression des donn??es **COMPRESSION_OF_DATA**. Elle va prendre en entr??e le dictionnaire des solutions HF **COLLECTION_SOLUTIONS_CAS**. Elle va ensuite d??terminer un espace vectoriel de dimension r??duite (ou une vari??t?? de dimnension r??duite, pour les m??thodes non lin??aires), mat??rialis?? par une **BASE_ORDRE_REDUIT**, telle que la distance des solution ?? cet espace soit faible.

Dans un deuxi??me temps, une m??thode **COMPRESSION_OF_OPERATORS** va produire des op??rateurs de r??solution approch??e de complexit?? moindre, en prenant en entr??e des **RESOLUTION_DATA_OBJECT** obtenus ?? l'??tape 1 ainsi que la **BASE_ORDRE_REDUIT**, afin de produire des **REDUCED_RESOLUTION_DATA**.

Enfin, l'objet r??sultat final **CAS_REDUIT_A_RESOUDRE** est "assembl??" ?? partir:

   * d'un **REDUCED_SOLVER_DATASET** qui sera copi?? depuis la **REDUCTION_PROCEDURE**, ??ventuellement adapt?? ??galement ?? partir d'un *template* comme cette derni??re;

   * de la **BASE_ORDRE_REDUIT**

   * du **CASE_DATA** afin d'avoir les informations pour qualifier le probl??me et sa variabilit??

   * des **REDUCED_RESOLUTION_DATA**.

.. todo::

    Montrer dans le mod??le de donn??es que **REDUCED_SOLVER_DATASET** est contenu dans la **REDUCTION_PROCEDURE**. 

Pour ??tre plus exhaustif sur les diff??rents algorithmes possibles et leur usage des donn??es, on pourra se r??f??rer au tableau d??di??. 

B.02 - Comparer un mod??le r??duit romA avec un mod??le haute-fid??lit?? A
---------------------------------------------------------------------

L'utilisateur B va commencer ?? reconstruire la solution en utilisant le use case A.04, ce qui va transformer la **SOLUTION_REDUITE_CAS** en **INDEXED_SOLUTION** :math:`u_r`.

Puis le syst??me va comparer deux **INDEXED_SOLUTION** (une *reconstructed* et une *high-fidelity*) ?? l'aide d'une m??thode **COMPARISON_OF_FIELDS** qui a acc??s ?? **COLLECTION_SOLUTION_CAS** et peut donc:

    * acc??der aux solutions disponibles par valeurs de param??tres. Pour ??tre s??r de comparer des solutions ?? valeur de param??tre ??gale, il faut que les solutions *reconstructed* soit index??es comme les solutions *high-fidelity*, et par cons??quent, il faut en amont que les **SOLUTION_REDUITE_CAS** aient ??t?? index??es de cette fa??on: c'est une exigence sur le use case A.04.

    * disposer d'une *scalar_product_matrix* :math:`K`

Ceci va produire un **QUALITY_INDICATOR** de type *a priori error*. Cet indicateur calcule :math:`\dfrac{\| u_r - u \|}{\| u \|}` avec :math:`\| u \| = u^T K u`.

.. todo::

   Ajouter cet acc??s des solutions r??duites par valeur de param??tre dans le mod??le de donn??es

B.03 - Comparer un mod??le r??duit romA avec un mod??le haute fid??lit?? B
---------------------------------------------------------------------

Plusieurs cas de figure:

   * soit les r??sultats des mod??les haute-fid??lit?? A et B ont la m??me structure, et on peut alors appliquer tel quel B.02

   * soit pas, et on va alors comparer des **QUANTITY_OF_INTEREST** de A et B dont l'utilisateur estime qu'elles doivent ??tre semblables entre les deux mod??les.

Pour cr??er la **QUANTITY_OF_INTEREST** issue de A, on fait appel au use case A.11. On fait ensuite appel ?? une m??thode **COMPARISON_OF_SIGNALS** qui compare deux **QUANTITY_OF_INTEREST** (r??duites ou non) et produit un indicateur scalaire **QUALITY_INDICATOR**, qui sera de type *validation with other computation* pour ce use case.

B.04 - Comparer un mod??le r??duit romA avec des exp??riences (validation)
-----------------------------------------------------------------------

Idem que B.03, l'indicateur produit est de type *validation with experimental data*.

B.05 - Faire interagir un mod??le r??duit et des op??rations de Data Science, typiquement pour obtenir un estimateur d'??tat
------------------------------------------------------------------------------------------------------------------------

Dans ce use case, on souhaite utiliser un mod??le r??duit avec des m??thodes d'assimilation de don??es. L'ojectif est d'obtenir un estimateur d'??tat sur la base:

   * des m??thodes PBDW ou GEIM;

   * de m??thodes variationnelles (3D-Var, 4D-Var) ou de contr??le optimal.

Commen??ons par le premier cas, on suppose que la s??lection de la base r??duite et des capteurs est r??alis??e par le use case A.12, qui peut ??tre vu comme la "phase offline" de la m??thode. Reste donc la phase online ?? effectuer.

Pour cela, il faut donc une **BASE_ORDRE_REDUIT** et des **QUANTITY_OF_INTEREST_STRUCTURE** afin d'avoir la forme lin??aire permettant de reconstruire les signaux ?? partir des champs. Typiquement, la phase online consiste ?? r??soudre un petit syst??me lin??aire (taille de la base r??duite + nombre de mesures). La phase *offline* peut avoir pr??-calcul?? certains op??rateurs en tant que **REDUCED_RESOLUTION_DATA**, par exemple la matrice de ce syst??me et sa factorisation.

Dans le second cas, on r??soud un probl??me qui couple les op??rateurs du mod??le r??duit (dont les op??rateurs sont en g??n??ral suppos??s lin??aires ?? param??tre donn??), les mesures et les formes lin??aires qui localisent les mesures. Donc on a une proc??dure qui couple **REDUCED_RESOLUTION_DATA**, **QUANTITY_OF_INTEREST** et **QUANTITY_OF_INTEREST_STRUCTURE**.

Dans ce seond cas, la phase *offline* doit donc ??galement ??tre trait??e par ce use case. On peut imaginer qu'on part d'une **REDUCTION_PROCEDURE** existante, et on y ajoute des op??rateurs mixte mod??le donn??es et une nouvelle proc??dure de r??duction online.

.. todo::

   Concr??tement, compression of operators doit donc pouvoir acc??der aux **QUANTITY_OF_INTEREST_STRUCTURE** qui d??finissent le lien (forme lin??aire) entre champs et mesures.

B.06 - Utilisation in-situ pour acc??l??rer la convergence du solveur non-lin??aire HF
-----------------------------------------------------------------------------------

Ce cas test est tr??s intrusif (codage dans le solveur en question) et potentiellement impactant. Il n'est pas inclus dans le mod??le du domaine actuellement.

B.07 - Cr??ation d'un mod??le r??duit pour un nouveau cas m??tier ?? partir d'un template existant de m??thodologie de r??duction
--------------------------------------------------------------------------------------------------------------------------

Identique ?? B.01 sauf qu'on donne explicitement les m??thodes **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS** ?? utiliser au lieu de les tester parmi celles disponibles (c'est donc plus simple).

B.08 - Utilisation d'un mod??le r??duit dans une boucle d'optimisation ou d'incertitude
-------------------------------------------------------------------------------------

Ce cas appelle A.13, il s'agit d'appeler un mod??le r??duit ?? la place d'un mod??le complet pour le traitement d'incertitude ou d'optimisation. Il faut que le code d'optimisation ou d'incertitude puisse ??valuer le mod??le r??duit comme s'il s'agissait du mod??le complet.

Difficile d'en tirer des conclusions g??n??riques sur un format d'export du mod??le r??duit tant les codes d'optimisation ou de traitement d'incertitudes sont vari??s, et tant les fa??ons d'appeler le comd??le complet sont vari??es.

C - Utilisateur sachant ??tablir un mod??le r??duit
================================================

C.01 - Cr??ation d'un mod??le r??duit en choisissant la m??thode, pour un probl??me ?? variabilit?? param??trique
---------------------------------------------------------------------------------------------------------

On rappelle les 5 ??tapes de la cr??ation d'un mod??le r??duit de B.01:

    1. l'utilisateur fournit les information pour caract??riser le probl??me et sa variabilit??;

    2. l'utilisateur r??cup??re ou fait calculer par le solveur haute-fid??lit?? les op??rateurs HF qui sont des donn??es d'entr??e pour la phase d'apprentissage;

    3. l'utilisateur r??colte et caract??rise les r??sultats haute-fid??lit?? depuis des fichiers r??sultats;

    4. l'utilisateur *??crit* la phase d'apprentissage (phase offline);

    5. le syst??me effectue la phase d'aprentissage et produit les objets constituant le mod??le r??duit **CAS_REDUIT_A_RESOUDRE**.

La seule diff??rence avec B.01 est l'??tape 4: cette fois-ci, plut??t que d'adapter ?? la marge un template, l'utilisateur C ??crit sa phase d'apprentissage, ??ventuellement en r??utilisant ?? certaines ??tapes des m??thodes de **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS** existantes par ailleurs dans la biblioth??que ou ses modules.

*Cas o?? l'utilisateur C souhaite enregistrer son code comme template*

    * on doit qualifier les informations qui seront ?? compl??ter par B.07 (leur type et leur r??le)

    * on doit enregistrer le template. Dans un premier temps en vue de la prochaine sortie de version de Mordicus, au moins dans la sortie de version pour un partenaire en question, avec son environnement logiciel propre. Dans un second temps dans une base de donn??es commune ?? tous ?

*Notes:*

    * ?? propos de l'??criture d'un reader pour 2 et 3: l'utilisateur se conforme ?? une API avec des entr??es et des sorties oblig??es (ms il peut en rajouter)

    * les phases 2 - 5 peuvent faire appels ?? des outils externes **EXTERNAL_SOLVING_PROCEDURE** qui viennent avec leur environnement logiciel, et peuvent ??tre propri??taires ou non (exemple ZSet, Medcoupling...). La proc??dure "d'enregistrement" d'une **EXTERNAL_SOLVING_PROCEDURE** doit ensuite permettre de construire Mordicus avec les d??pendances correspondantes, de sorte que chaque partenaire du projet puisse ensuite construire Mordicus de fa??on diff??renci??e selon les **EXTERNAL_SOLVING_PROCEDURE** qui ont ??t?? enregistr??es.

C.02 - Cr??ation d'un mod??le r??duit en choisissant la m??thode, pour un probl??me ?? variabilit?? non param??trique
-------------------------------------------------------------------------------------------------------------

L'utilisateur renseigne un **VARIABLE_PARAMETER** avec un type qui n'est pas *float* mais peut ??tre n'importe quel **RESOLUTION_DATA_OBJECT**. Il n'y a alors pas de *design of experiments*, directement un **PARAMETER_VALUE** qui met en lien la valeur avec une *string* unique pour l'identifier.

.. todo::

   Ajouter tout ??a dans le mod??le de donn??es, qui jusqu'alors ??tait ??crit pour le cas param??trique uniquement

C.03 - Cr??ation d'un mod??le r??duit en choisissant la m??thode, pour un probl??me ?? variablit?? mixte param??trique / non param??trique
---------------------------------------------------------------------------------------------------------------------------------

Combinaison naturelle de C.01 et C.02, le *support d'indexation* ne s'applique qu'aux param??tres r??els.

C.04 - Cr??ation d'un mod??le r??duit ?? partir de mesures ou de signaux I/O d'un mod??le inconnu
--------------------------------------------------------------------------------------------

Dans ce cas, il n'y a pas de solveur ni de **RESOLUTION_DATA_OBJECT**, la m??thode **COMPRESSION_OF_OPERATORS** (on devrait plut??t dire *construction of operators* dans ce cas) repose uniquement sur des **INDEXED_SOLUTIONS**.

C.05 - Faire calculer une nouvelle simulation HF par le solveur "?? la vol??e" pour une proc??dure de r??duction qui le demande (bas niveau)
----------------------------------------------------------------------------------------------------------------------------------------

C'est le cas notamment de toutes les m??thodes o?? l'??chantillonage se fait de fa??on incr??mentale. On doit faire calculer par **REDUCTION_PROCEDURE** de nouvelles **INDEXED_SOLUTION**. On utilise pour cela le lien de **REDUCTION_PROCEDURE** ?? **CASE_DATA**.

Pour ??a, on doit avoir "d??clar??" au registre de Mordicus le solveur externe. On peut noter deux types de d??claration, selon qu'on envisage d'utiliser ou non le solveur sur la dur??e:

   * enregistrement uniquement pour la dur??e de la session Mordicus (peut-on dire *enregistrement dynamique*?),

   * enregistrement durable pour construire Mordicus en lien avec le solveur (*enregistrement statique*). Le solveur sera alors disponible ?? la prochaine sortie version de Mordicus *du partenaire* (avec ses modules et d??pendances). Au passage, cela signifie qu'il faut pouvoir avoir une proc??dure de construction diff??renci??e pour chaque partenaire.

Cette d??claration prend la forme d'un objet **EXTERNAL_SOLVING_PROCEDURE** l??ger qui contient des informations pour savoir comment appeler le solveur pour :

   * cette session en particulier dans le *cas dynamique*;

   * cette installation de Mordicus en particulier dans le *cas statique*.

Ces informations sont typiquement: des variables d'environnement, un chemin d'installation, un script de lancement...

L'appel au solveur est fait via une API impos??e, afin de pouvoir changer de solveur sans changer le code de la **REDUCTION_PROCEDURE**. Il faut donc adapter:

   * les entr??es: **INDEXATION**, **SOLVER_DATASET**

   * les sorties: **INDEXED_SOLUTIONS**

On va donc trouver dans les m??thodes de **EXTERNAL_SOLVING_PROCEDURE** des *adaptateurs*, ?? ??crire par l'utilisateur C qui d??clare ce solveur:

   * permettant l'appel au solveur avec les donn??es de **SOLVER_DATASET** et **INDEXATION**, et les informations de **EXTERNAL_SOLVING_PROCEDURE**

   * permattant la conversion des r??sultats du format du solveur en **INDEXED_SOLUTION** de Mordicus.

C.06 - Modifier un mod??le r??duit pour (i) int??grer de nouvelles informations ou (ii) appliquer un niveau de r??duction suppl??mentaire
------------------------------------------------------------------------------------------------------------------------------------

Comme nous l'avons d??j?? dit, une proc??dure de r??duction se compose souvent d'une premi??re phase de compression des donn??es et une seconde phase de compression des op??rateurs. Parfois, on peut d??j?? obtenir un mod??le r??duit ?? partir de la phase de compression des donn??es et d'une compression des op??rateurs tr??s sommaire (et pas efficace). La r??duction se fait donc en deux temps, en appliquant un second niveau de r??duction ?? un **CAS_REDUIT_A_RESOUDRE** d??j?? existant.

.. todo::

   Ajouter dans le mod??le de donn??es que **COMPRESSION_OF_OPERATORS** peut travailler sur un **CAS_REDUIT_A_RESOUDRE**

Par ailleurs, il arrive qu'on veuille am??liorer l'approximation d'un **CAS_REDUIT_A_RESOUDRE** en incluant de nouvelles donn??es haute-fid??lit?? (qu'on vient de recevoir, par exemple).

Dans ce cas, la m??thode **COMPRESSION_OF_DATA** vient enrichir en place la **BASE_ORDRE_REDUIT**, puis la m??thode **COMPRESSION_OF_OPERATORS** vient enrichir en place les **REDUCED_RESOLUTION_DATA**. C'est ce qui est fait pour chaque **INDEXED_SOLUTION** par les algorithmes incr??mentaux.

L'int??r??t de proc??der de la sorte (construire **CAS_REDUIT_A_RESOUDRE** incr??mentalement par des modifications en place, et non ?? la fin) est que si une it??ration ??choue, on dispose toujours du mod??le r??duit construit jusqu'alors.

C.07 - Permettre le calcul multi-??chelles ou multi-physiques de syst??mes repr??sent??s par des mod??les r??duits
------------------------------------------------------------------------------------------------------------

On peut distinguer deux cas de figure:

    * on dispose de cette m??me physique multi-repr??sent??e avec des mod??les complet, et un couplage logiciel fonctionnel,

    * on n'en dispose pas.

Dans le premier cas, l'utilisateur cherchera sans doute ?? conserver le cha??nage logiciel existant et ?? remplacer les appels aux solveurs complets par des appels ?? Mordicus. Compte-tenu des nombreuses fa??on possibles d'appeler un solveur, c'est hors cadre de Mordicus (comme B.08).

En ce qui concerne le second cas, concr??tement, un **CAS_REDUIT_A_RESOUDRE** contient alors plusieurs **REDUCED_SOLVER_DATASET**. A propos de l'impact sur le mod??le de donn??es, tout d??pend de ce qui est transmis dans ce cha??nage: **VECTOR_OF_UNKNOWNS** (par exemple un chargement), **MATRIX**, **FIELD** (temp??ratures en entr??e d'un calcul m??canique)..., qui sont ?? un format r??duit (sinon on retombe sur le premier cas).

Le probl??me est alors la coh??rence s??mantique des donn??es qui sont transf??r??es, exemple:

   * **FIELD** du mod??le 1 qui a une base dans le mod??le 2 ms qui vivent sur des maillages diff??rents ou dans des bases diff??rentes (IFS). Il faut arriver ?? les projecter d'une base ?? une autre, et pour cela repasser faire des projections de champs via les **APPROXIMATION_SPACE** des maillages complets est le plus s??r. Pour cela, on doit d??clarer ?? l'utilitaire qui fait les projections de champs (par exemple Medcoupling) les caract??ristiques des **APPROXIMATION_SPACE** (??l??ment de r??f??rence, coordonn??es de r??f??rences des points des Gauss, poids de r??f??rence des points de Gauss) des mod??les complets. Si la localisation des champs ?? tranf??rer est toujours la m??me, cela peut ??tre fait en offline, on peut assimiler ??a ?? une **COMPRESSION_OF_OPERATORS**.

   * **FIELD** du mod??le 1 qui n'a pas de base dans le mod??le 2 (temp??rature donn??e en entr??e d'un calcul m??canique). En g??n??ral, il suffit de transf??rer ce champ sur le sous-maillage (points de quadrature empirique, de l'EIM...) utile ?? la r??solution offline. Si la localisation ne change pas, c'est un op??rateur lin??aire, et ??a peut ??tre fait en *offline* (avec les m??mes informations que le cas pr??c??dent).

C.08 - Affichage ergonomique des informations contenues dans le mod??le r??duit (bases etc)
-----------------------------------------------------------------------------------------

Visualisation des **REDUCED_RESOLUTION_DATA** (base r??duite y compris) pour d??bugger. Chaque partenaire est libre de l'impl??menter dans son viewer sur la base d'une API commune, laquelle d??pendra forc??ment de la s??rialisation de A.07.

C.09 - Construire un mod??le r??duit 3 en combinant deux mod??les r??duits 1 et 2 du m??me syst??me
---------------------------------------------------------------------------------------------

*Voir par exemple le cas vers?? par Safran dans la maquette*

Dans ce cas d'usage, pour un seul **CAS_REDUIT_A_RESOUDRE** et un seul **REDUCED_SOLVER_DATASET**, on a plusieurs **BASE_ORDRE_REDUIT** et m??me plus largement plusieurs **REDUCED_RESOLUTION_DATA** que l'on s??lectionne en fonction de la r??gion du domaine param??trique dans laquelle on se trouve.

La s??lection se fait sur la base d'une **FUNCTION_OF_PARAMETERS** (avec ??ventuellement le temps comme argument suppl??mentaire).

Cette structure peut ??tre construite comme telle ?? la base (pr??vu dans l'algorithme de la **REDUCTION_PROCEDURE**), ou construit ?? partir de deux **CAS_REDUIT_A_RESOUDRE** se basant sur un m??me **CASE_DATA**. Il faut dans ce cas que les **CAS_REDUIT_A_RESOUDRE** originaux contiennent chacun un **SUPPORT_INDEXATION** indiquant leur domaine de validit??, lequel peut ??tre produit dynamiquement par des algorithmes de classification. Le **CAS_REDUIT_A_RESOUDRE** sera obtenu en fusionnant les deux domaines.

Il faut ajouter dans le **REDUCED_SOLVER_DATASET** des **REDUCED_RESOLUTION_DATA** particulier permettant de faire le passage de la solution r??duite d'une repr??sentation (une **BASE_ORDRE_REDUIT**) ?? une autre quand on change de r??gion en cours de calcul online.

.. todo::

   Ajouter ce qui pr??c??de dans le mod??le de donn??es

C.10 - ??valuer l'int??r??t de la d??marche "Offline+Mod??le r??duit" par rapport ?? l'utilisation directe du mod??le haute fid??lit??
----------------------------------------------------------------------------------------------------------------------------

Ce cas d'usage se pr??sente quand on anticipe un petit nombre d'??valuations du mod??le r??duit. On doit pouvoir mesurer le temps CPU d'un appel du mod??le complet et le temps CPU de l'appel ?? la **REDUCTION_PROCEDURE** (phase offline) + appel au mod??le r??duit. Peut se faire dans le noyau de Mordicus, pas vraiment d'impact sur le mod??le de donn??es.

C.11 - Construire un mod??le r??duit lorsque le maillage (voire la g??om??trie) change entre les diff??rents snapshots
-----------------------------------------------------------------------------------------------------------------

Diff??rent de A.10 dans le sens o?? on veut compresser des *solutions* qui ne vivent pas sur le m??me maillage. Pour cela, il faut que l'utilisateur applique un op??rateur de *morphing* pour ramener tous les snapshots sur le m??me maillage de r??f??rence (*reference_support*).

Ce morphing est a priori hors du mod??le de donn??es de Mordicus. N??anmoins, il peut entrer dans la composition de la **REDUCTION_PROCEDURE**. Il est alors impl??ment?? comme une **STANDARD_FUNCTION_IMPLEMENTATION** par l'utilisateur C d??veloppeur.

C.12 - Utilisation d'it??r??s de calcul comme snapshots pour effectuer la r??duction
---------------------------------------------------------------------------------

Dans ce use case, c'est le code de calcul qui appelle les API de Mordicus et non l'inverse.

Ce les choix technologiques, cela plaide pour une impl??mentation du noyau en C++. En ce qui concerne le mod??le de donn??es, on ne peut pas pr??voir la faisabilit?? de l'appel depuis n'importe quel code de calcul (il y en a ??norm??ment, et on ne ma??trise par leur structure), il faut uniquement pr??voir des **INDEXED_SOLUTION** qui se sont pas index??es par les valeurs de param??tre ms uniquement par un num??ro d'ordre *ordinal_number*.

C.13 - Cr??ation d'un mod??le r??duit ?? partir d'un DoE d??j?? disponible (et sans possibilit?? de faire de nouveaux calculs HF)
--------------------------------------------------------------------------------------------------------------------------

Ce use case est pr??vu par le mod??le de donn??es: le **CASE_DATA** n'a pas de **SOLVER_DATASET**. On ne peut pas calculer de **RESOLUTION_DATA_OBJECT** n??cessitant un appel au code de calcul, donc ceux que la m??thode de r??duction demande doivent pouvoir ??tre d??duit du seul **DISCRETE_SUPPORT**.

C.14 - D??velopper / brancher dans Mordicus une nouvelle m??thodologie de r??duction de mod??les ou une variante d'une m??thode existante
------------------------------------------------------------------------------------------------------------------------------------

L'utilisateur C d??veloppeur doit impl??menter une **REDUCTION_PROCEDURE** ou une **REDUCTION_PROCEDURE_TEMPLATE**. Il peut appeler les **COMPRESSION_OF_DATA** et **COMPRESSION_OF_OPERATORS** disponibles dans la biblioth??que. La **REDUCTION_PROCEDURE** prend un **CASE_DATA** et des **RESOLUTION_DATA_OBJECTS** en entr??e et produit un **CAS_REDUIT_A_RESOUDRE**.

Il adapte la proc??dure de construction de Mordicus de son entit?? (avec les modules de son entit?? et ceux dont la PI est disponible) par rapport aux d??pendances de cette **REDUCTION_PROCEDURE**. 

Idem pour l'??crite d'une **INTERNAL_SOLVING_PROCEDURE** dont l'??criture se fait sans API normalis??e. C'est a priori le **CAS_REDUIT_A_RESOUDRE** qui sait comment appeler **INTERNAL_SOLVING_PROCEDURE** en lui fournissant le **REDUCED_SOLVER_DATASET** dont il a besoin.


C.15 - G??n??rer une base r??duite ?? partir d'un jeu de donn??es de simulation (cas plus bas niveau)
------------------------------------------------------------------------------------------------

Ceci est mat??rialis?? par l'op??ration **COMPRESSION_OF_DATA** du mod??le de donn??es, elle prend en entr??e un objet **COLLECTION_SOLUTION_CAS** contenant les donn??es de simulation et produit un objet **BASE_ORDRE_REDUIT**. 

Les **INDEXED_SOLUTION** de la **COLLECTION_SOLUTION_CAS** (en entr??e) et les **VECTEUR_BASE_ORDRE_REDUIT** de la **BASE_ORDRE_REDUIT** (en sortie) ont la m??me **OUTPUT_DESCRIPTION** (m??me gradeur physique, m??me structures des champs etc.)

Cette op??ration peut ??tre incr??mentale (voir C.06), auquel cas **COMPRESSION_OF_DATA** vient enrichir en place la **BASE_ORDRE_REDUIT**, qui fait alors ??galement partie des entr??es.

C.16 - Enrichir un plan d'exp??rience ?? partir d'un premier jeu de donn??es de simulation
---------------------------------------------------------------------------------------

Dans ce use case, on imagine que l'utilisateur C a d??j?? fait tourner une **REDUCTION_PROCEDURE** sur un premier jeu de simulations compl??tes, correspondant ?? un ensemble de valeurs des param??tres (objet *available_values* de **SUPPORT_INDEXATION**). Cette **REDUCTION_PROCEDURE** peut proc??der en utilisant les ??quations de la physique ou ??tre une proc??dure simplifi??e de r??gression statistique qui tourne tr??s rapidement. Il souhaite ?? pr??sent enrichir **COLLECTION_SOLUTION_CAS** avec de nouvelles simulations, choisies pour apporter un maximum d'information en un minimum de tirages. Il va pour cela exploiter le **CAS_REDUIT_A_RESOUDRE** issu de cette reduction procedure pour produire un *design_of_experiments* dans **SUPPORT_INDEXATION**.

Cas 1: pour la **REDUCTION_PROCEDURE**, on dispose d'un indicateur de qualit?? *a posteriori*. On va alors faire tourner le **CAS_REDUIT_A_RESOUDRE** sur un ensemble large (c'est l'attribut *training_set* de **SUPPORT_INDEXATION**), et choisir pour le *design_of_experiments* les :math:`N` valeurs pour lesquelles l'indicateur *as posteriori* est le plus ??lev??, avec souvent des indicateurs de distance en plus entre les valeurs, pour ne pas toutes les choisir dans la m??me r??gion.

Cas 2: on se base sur des indicateurs statistiques (typiquement le maximum de l'estimation de la variance d'un mod??le de r??gression statistique) pour choisir ces valeurs. Au niveau du mod??le de donn??es, c'est la m??me chose que le Cas 1, sauf que le **CAS_REDUIT_A_RESOUDRE** est issu d'une m??thode statistique et poss??de un **QUALITY_INDICATOR** de type *estimated_variance*.

C.17 - Appeler une fonction utilisateur ou du code utilisateur lors de la phase online (bas niveau)
---------------------------------------------------------------------------------------------------

Dans ce cas d'usage, la m??thode de r??solution **INTERNAL_SOLVING_PROCEDURE** qui est utilis??e lors de l'??valuation d'un mod??le r??duit ne prend pas en arguments uniquement des objets *statiques* (un vecteur, une matrice... je ne sait pas si le vocabulaire est le bon), mais ??galement des fonctions fournie par l'utilisateur C au cours de C.01 ou C.02. Typiquement, cela va ??tre le cas quand la **INTERNAL_SOLVING_PROCEDURE** doit appeler une loi de comportement externe.

Dans ce cas, l'utilisateur C va d??clarer "un blanc" au moment de d??velopper son **INTERNAL_SOLVING_PROCEDURE** (use case C.14), l'interface de la fonction ?? fournir ??tant sp??cifi??e par une **STANDARD_FUNCTION_DECLARATION**. 

L'appel de la **STANDARD_FUNCTION_IMPLEMENTATION** doit ??tre autoportante quand l'utilisateur A r??cup??re le mod??le r??duit.

R??capitulons le d??roulement de l'utilisation d'une fonction utilisateur:

   * C.14: l'utilisateur C d??veloppeur d??veloppe une proc??dure de r??solution pour un type de mod??le r??duit, il d??clare certains blancs ?? remplir par des fonctions utilisateurs dans son algorithmes par les **STANDARD_FUNCTION_DECLARATION**

   * C.01 ou C.02: l'utilisateur C g??n??re un **CAS_REDUIT_A_RESOUDRE**, il fournit dans la **RESOLUTION_PROCEDURE** la fonction utilisateur **STANDARD_FUNCTION_IMPLEMENTATION** ?? utiliser

   * A.13: la **STANDARD_FUNCTION_IMPLEMENTATION** est appel??e par le **CAS_REDUIT_A_RESOUDRE** qui a ??t?? r??cup??r?? par l'utilisateur A 


C.18 - Construire une base r??duite distribu??e en m??moire (par DD) ?? partir de donn??es de calcul distribu??es en m??moire
----------------------------------------------------------------------------------------------------------------------

A mettre en lien avec A.05.

Du point de vue de la compression des donn??es **COMPRESSION_OF_DATA**:

    * le maillage est distribu?? sur les sous-domaines: chaque processeur poss??de un maillage **DISCRETE_SUPPORT** qui est le maillage du sous-domaine;

    * les r??sultats de type **FIELD** sont distribu??s par sous-domaine sur les processeur, ainsi que les modes **VECTEUR_BASE_ORDRE_REDUIT** de type **FIELD**.

Pour les algorithmes MPI de **COMPRESSION_OF_DATA** (typiquement snapshot-POD), les op??rations principales sont des int??grales (op??rateurs d'auto-corr??lation, projection sur une base...) qui peuvent ??tre calcul??es par sous-domaine et somm??es, de sorte qu'il n'est pas besoin pour cette ??tape de disposer de la correspondance de num??rotation locale -> globale du maillage et des champs.

Du point de vue de la compression des op??rateurs **COMPRESSION_OF_OPERATORS**, cette distribution de donn??es est faite de la m??me fa??on. En revanche, la m??thode **COMPRESSION_OF_OPERATORS** calcule des **REDUCED_RESOLUTION_DATA** par *sous-domaine*, lesquels doivent ensuite ??tre "rassembl??s" (selon une logique ?? coder par le d??veloppeur de la m??thode) en un **REDUCED_RESOLUTION_DATA** final, car le mod??le r??duit final tourne sur un seul processeur. Cette op??ration de "rassemblement" fait presque toujours appel ?? la correspondance de num??rotation local -> global.

Par exemple, une proc??dure type quadrature empirique ou hyperr??duction va produire un maillage r??duit par sous-domaines, lesquels doivent ensuite ??tre assembl??s en un unique maillage r??duit.

C.19 - Garantir qu'un mod??le r??duit conserve certaines propri??t??s math??matiques du mod??le haute fid??lit?? sur un sous-domaine
----------------------------------------------------------------------------------------------------------------------------

A mettre en lien avec A.09.

L'utilisateur C doit d??velopper un **REDUCED_POSTPROCESSING_DATASET** ou un **REDUCED_POSTPROCESSING_DATASET_TEMPLATE** en m??me temps que le d??veloppement de la **REDUCTION_PROCEDURE** dans C.14. Comme d??crit dans A.09, le **REDUCED_POSTPROCESSING_DATASET** ?? droit en donn??es d'entr??e aux **REDUCED_RESOLUTION_DATA** du **CAS_REDUIT_A_RESOUDRE**, et ?? des **REDUCED_RESOLUTION_DATA** qu'il peut faire calculer par la proc??dure de r??duction.

A la fin de la **REDUCTION_PROCEDURE** (voir le use case B.01), le **QUALITY_INDICATOR** et **REDUCED_POSTPROCESSING_DATASET** sont int??gr??s ?? l'assmblage du **CAS_REDUIT_A_RESOUDRE**.

C.20 - G??rer une taille m??moire prescrite pour l'??laboration d'un mod??le r??duit
-------------------------------------------------------------------------------

Les m??thodes **COMPRESSION_OF_DATA** et **COMPRESSSION_OF_OPERATORS** poss??dent certaines options "de contr??le" (tol??rance de la SVD, taille de la base r??duite ?? produire, pr??cision de l'EIM...). L'id??e est d'utiliser les options de contr??le qui peuvent facilement ??tre reli??e ?? une estimation de la consommation m??moire (typiquement des tailles de bases ou nombres de fonctions dans une d??composition en s??rie d'une fonction). On ajuste it??rativement ces options de contr??le de fa??on ?? ne pas d??passer une consommation m??moire limite. 

Exemple type: on contr??le la taille de la base r??duite en estimant le co??t m??moire de g??n??rer vecteur suppl??mentaire dans la base.

Il faut pour cela que le d??veloppeur de la m??thode **COMPRESSION_OF_DATA** ait impl??ment?? une fonction d'estimation de la consommation m??moire en fonction de certaines options de contr??le, gr??ce ?? une analyse de complexit?? m??moire (m??me sommaire) de son algorithme. L'utilisateur peut alors param??trer sa **REDUCTION_PROCEDURE** en fonction de ces options de contr??le et contr??ler par ce biais la consommation m??moire avant de lancer la **REDUCTION_PROCEDURE**.
