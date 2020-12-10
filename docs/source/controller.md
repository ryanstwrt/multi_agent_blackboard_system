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
    * Description : Dictionary of agent names and agent types which will be used to solve the problem.
    * Default : {}
    * Note : Note the name for each agent must be unique.
    * Example : {'ka_mc' : karp.KaGlobal, 'ka_ns': karp.KaLocal, 'ka_lvl1': kabr.KaBr_lvl1}
* 