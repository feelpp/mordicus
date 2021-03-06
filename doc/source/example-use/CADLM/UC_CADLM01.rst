.. _UC_CADLM01:

CADLM Use Case
--------------

*Contexte à ajouter*

.. .. tabularcolumns:: |L|L|L|L|

.. table:: CADLM use case
  :class: longtable
  
  +---------------------+----------+------------------------+-------------------------------------------------+
  | USE CASE CADLM01    |   SLED TEST Evaluate the response of new parameter set from the data                |
  |                     |   generated by simulation                                                           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Context of use      |   Users simulate their problems with various parameter set. Nodal value will be     |
  |                     |   saved as training data. The solution of new parameter set is evaluate by using    |
  |                     |   model reduction.                                                                  |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Scope               |   The model reduction module of ODYSSEE                                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Level               |   Primary task                                                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Primary actor       |   User with knowledge of the physics problem, knowledge of model reduction          |
  |                     |   is not necessary .                                                                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Stakeholders and    |   Stakeholders                    | Interests                                       |
  | interests           |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     |                                   |                                                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Preconditions       |  Have available:                                                                    |
  |                     |                                                                                     |
  |                     |     * Result fields or requested responses for all time steps.                      |
  |                     |                                                                                     |
  |                     |     * The DoE used for generating the results/ responses.                           |
  |                     |                                                                                     |
  |                     |     * New parameter set to evaluate results/ response.                              |
  |                     |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Success end cond    |  The expected data is produced                                                      |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Failed end          |  Process is terminated, users get informed about computation time-out.              |
  | protection          |                                                                                     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Trigger             |  Users enter the model reduction module of ODYSSEE                                  | 
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Description         | Step     | Action                                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1        | Users fill the requested inputs : 3 csv files                            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 2        | A X.csv file which contains the DoE data for generating the training     |
  |                     |          | data (input)                                                             |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3        | A Y.csv file which contains output training data (output)                |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 4        | A XN.csv file which contains the new parameter set used to evaluate      |
  |                     |          | the predictedd results (new_input->new_output)                           |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 5        | Users demand the execution of the module to obtain new_output            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 6        | System verifies if the provided data is valid                            |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 7        | System generates the reduced model from input and output                 |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 8        | System computes the response of new set of parameter (new_output)        |
  |                     |          | and save in a csv file                                                   |
  +---------------------+----------+------------------------+-------------------------------------------------+
  | Extensions          | Step     | Branching action                                                         |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 1a       | Submitted data is corrupted or wrong format : Notification for users     |
  +---------------------+----------+------------------------+-------------------------------------------------+
  |                     | 3b       | Non matching dimensions between input files: notification for users      |
  +---------------------+----------+------------------------+-------------------------------------------------+
