# Controller

The controller organizes the problem, controls the problem flow, and allocates resources for knowledge source to preform an action.
Organizing and controlling the problem flow requires the controller to assess how each knowledge source can contribute to the problem.
This process is performed via a triggering system with the BA, where knowledge sources respond to the trigger with a trigger value (some numerical value) to indicate their ability to contribute to the problem.
Based on this information, the BA selects the knowledge source which can provide the most information to the problem (typically has the highest trigger value) and selects them to perform their action.
This provides a level of structure for solving the problem and allows for a centralized unit to determine the best type of knowledge source to be run at a given time.

When initializing the `controller`, there are a number of keywords arguments that the user can pass to update the blackboard problem.

## Keyword Arguments

* bb_name (str):
    * Description : Name of the BA
    * Default :' bb'
* bb_type (bb object):
    * Description : BA object which we want to perform the optimization process.
    * Default : blackboard.Blackbaord
* ka (dict):
    * Description : Dictionary of agent names and agent class name which will be used to solve the problem.
    * Default : {}
    * Note : The name for each agent must be unique.
    * Example : ```{'ka_mc' : karp.KaGlobal, 'ka_ns': karp.KaLocal, 'ka_lvl1': kabr.KaBr_lvl1}```
* design_variables (dict):
    * Description : Dictionary of design variables to be used in optimization problem.
    * Default : None 
    * Note : See [BA](blackboard.md) for design variable formatting.
    * Example : ```{'dv_example': {'ll': 0.0, 'ul', 1.0, 'variable type': float}}```
* objectives (dict):
    * Description : Dictionary of objectives to be used in optimization problem.
    * Default : None 
    * Note : See [BA](blackboard.md) for objective formatting.
    * Example : ```{'obj_example': {'ll': 0.0, 'ul', 1.0, 'goal': 'lt', 'variable type': float}}```
* constraints (dict):
    * Description : Dictionary of constraints to be used in optimization problem.
    * Default : None 
    * Note : See [BA](blackboard.md) for constraint formatting.
    * Example : ```{'constraint_example': {'ll': 0.0, 'ul', 1.0, 'variable type': float}}```
* archive (str):
    * Description : Name of the H5 file for storing the blackboard.
    * Default : bb_archive
* agent_wait_time (float):
    * Description : Time limit that the BA waits to recieve a trigger value form agents before sending another trigger event.
    * Default : 30
    * Note : Units are in seconds
* plot_progress (bool):
    * Description: If set to true, MABS plots the Pareto front, and hypervolume indicator at every `interval` in the convergence model.
    * Default : False
* convergence_model (dict):
    * Description : Dictionary for the convergence model to be used in this optimization problem. See [BA](blackboard.md) for full description.
    * Default ```{'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'skipped tvs': 200, 'total tvs': 1E6}```
* surrogae_model (dict):
    * Description : Dictionary detailing the surrogate model type and a pickle file where the surrogate model can be found.
    * Default : ```{'sm_type': 'lr', 'pickle file': None}```
    * Note : The surrogate model currently must be build using the `train_surrogate_model` module in MABS.
* random_seed (float/int):
    * Description : Random seed for all agents to start with (allows for mostly reproducable results)
    * Default : None