# Knowledge Agents - Search (KA-S)

KA-S agents are used to search the design space to find areas of interest and search for optimal solutions.
KA-S agent can be broken into two categories of search agents: global and local.
We will detail each type of global/local agent in detail and describe attributes that can be updated to differentiate agents and increase the overall systems ability to find solutions.

## KA-S Global

### KaGlobal

The `KaGlobal` agent utilizes a stocahstic method for determine each design variable.
If the design variable is a `float`, we select a value between the `ll` and `ul`.
If the design variable is a `list`, we randomly select a value form the `options`, if a random number is higher than the `learning_factor`, otherwise we select the `default option`

* learning_factor (float):
    * Description : Value for determining if we select the `default` or a design variable from `options`.
    * Default : 0.5
    * Note : Random number generators are between 0 and 1, so a `learning_factor` of 0 will always select from `options`.

### KaLHC

The `KaLHC` agent generates a latin hypercube distribution for all of the design variables. 
This will search the space in a more uniform manor than the stochastic method in `KaGlobal`.

* samples (int):
    * Description : Number of designs we want in our latin hypercube.
    * Default : 50
    * Note : We currently generate the latin hypercube when we initialize the agent. If the samples value is updated, we must run the agent methd `generate_lhc` to update the hypercube.

## KA-S Local

All KA-S local agent utilize designs found on the `Pareto Level` of the blackboard to search for more optimal solutions.
The BA sends the Pareto level to each KA-S agent, where the KA-S agent uses the design data and attempts to find additional areas of interest.

* learning_factor (float) :
    * Description : Value for determining if we select the design in the `Pareto level` with the highest fitness function, or a random design.
    * Default : 0.5
    * Note : Random number generators are between 0 and 1, so a `learning_factor` of 0 will always select a random design.
    
### KaLocal

The `KaLocal` agent utilizes a neighborhood search algorithm to search solutions around an already deemed optimal point.
The neighborhood search algorithm perturbs each design variable by the `perturbation_size`, in a positive and negative direction.
If the design variable is a list, we select a value from `options` that is not the current design variable.
 
* perturbation_size (float):
    * Description : Value for determining the size of perturbation to each design variable.
    * Default : 0.05
* neighboorhood_search (str):
    * Description : Determine if we apply a fixed perturbation, or a variable perturbation.
    * Default : fixed
    * Options : fixed, variable
    * Note : A variable perturbation applies a pertubation between 0 and `perutbation_size`.
    
### KALocalHC

The `KaLocalHC` agent uses a hill-climbing algorithm to each for optimal solutions.
We have two variations of hill-climbing algorithms currently available: simple and steepest-ascent.

The `simple` algorithm perturbs based on the `step_size` a variable, analyzes the objectives, and determines the change in objectives.
If the change in objectives is positive, it uses this new design and repeats this process.
If the change in objectives is not positive, it repeats the perurbation process until it finds a positive chnage in objectives.
If there is no positive step for the agent to make, we reduce the `step_size` by the `step_rate` and try again.
This process repeates until the `step_size` reaches the `convergence_cirteria` or we exceed the `step_limit`.

The `steepest-ascent` algorithm pertubes each design variable by the `step_size`.
Once all variables have been perturbed in a positive and negative direction, it selects the steepest gradient as the next step.
This process continues in a manner identical to the `simple` algorithm, and ends with either the `convergence_criteria` or `step_limit`.

* step_size (float):
    * Description : Value for determining the size of the perturbation to each design variable
    * Default : 0.1
* step_rate (float):
    * Description : Value for determing the rate at which we decrease the step size if no optimal values are present
    * Default 0.1
    * Note : If there is no positive gradient, we multiply the `step_size` by the `step_rate` to get the new `step_size`.
