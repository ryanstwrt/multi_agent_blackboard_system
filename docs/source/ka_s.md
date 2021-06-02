# Knowledge Agents - Search (KA-S)

KA-S agents are used to search the design space to find areas of interest and search for optimal solutions.
KA-S agent can be broken into two categories of search agents: global and local.
We will detail each type of global/local agent in detail and describe attributes that can be updated to differentiate agents and increase the overall systems ability to find solutions.

## KA-S Global

The following attributes are available for all KA-S global.

* execute_once (bool):
    * Description : If true, the agent can only be executed once. If `run_multi_agent_mode=True`, the agent will shutdown upon completing it's action.
    * Default : False
* run_multi_agent_mode (bool):
    * Description : If `execute_oncTreu`, the agent will only be executed once and then shutdown. If `run_multi_agent_mode=False`, the agent will remain active, but have a trigger value (TV) of 0 and will not be executed again.
    * Default : False
    * Note : This is required for running MABS in single_agent mode, as we require a TV from each agent.
* _design_accuracy (int):
    * Description : Set the accuracy we desire for our design variables.
    * Default : 5
* _objective_accuracy (int):
    * Description : Set the accuracy we desire for our objective functions.
    * Default : 5
* _constraint_accuracy (int):
    * Description : Set the accuracy we desire for our constraints.
    * Default : 5    

### Stochastic

The `Stochastic` agent utilizes a stocahstic method for determine each design variable.
If the design variable is a `float`, we select a value between the `ll` and `ul`.
If the design variable is a `list`, we randomly select a value form the `options`, if a random number is higher than the `learning_factor`, otherwise we select the `default` option.

* learning_factor (float):
    * Description : Value for determining if we select the `default` or a design variable from `options`.
    * Default : 0.5
    * Note : Random number generators are between 0 and 1, so a `learning_factor` of 0 will always select from `options`.

### LatinHypercube

The `LatinHypercube` agent generates a latin hypercube distribution for all of the design variables. 
This will search the space in a more uniform manor than the stochastic method in `KaGlobal`.

* samples (int):
    * Description : Number of designs we want in our latin hypercube.
    * Default : 50
    * Note : We currently generate the latin hypercube when we initialize the agent. If the samples value is updated, we must run the agent methd `generate_lhc` to update the hypercube.

* lhc_criterion (str):
    * Description : Determine how we set up the LHC sampling critera
    * Default : `corr`
    * Options: `corr`, `simple`
    * Note : Currently only two options are available, for more information on these, see [pyDOE](https://pythonhosted.org/pyDOE/).

## KA-S Local

KA-S locals agent utilize designs found on one of the blackboard abstract levels to search for more optimal solutions.
The BA sends the Pareto level to each KA-S agent, where the KA-S agent uses the design data and attempts to find additional areas of interest.
All attributes available to KA-S global agents are avaiable for KA-S local agents.

* learning_factor (float):
    * Description : Value for determining if we select the design in the `Pareto level` with the highest fitness function, or a random design.
    * Default : 0.5
    * Note : Random number generators are between 0 and 1, so a `learning_factor` of 0 will always select a random design.
* bb_lvl_read (int):
    * Description : Value for determining which abstract level the agenty will read from.
    * Default : 1
    * Note : `Pareto level`=1, `Viable Design Level`=1, `Data Level`=3
* reanalyze_designs (bool):
    * Description : Determine if we will keep a list of previously analyzed designs. If we false, we will only analyze each design once.
    * Default : False
    * Note : Setting this to true for KA-S agents which utilize some type of stochastic element can help improve the diverstiy of the Pareto front.
    
### NeighborhoodSearch

The `NeighborhoodSearch` agent utilizes a neighborhood search algorithm to search solutions around an already deemed optimal point.
The neighborhood search algorithm perturbs each design variable by the `perturbation_size`, in a positive and negative direction.
If the design variable is a list, we select a value from `options` that is not the current design variable.
We can perturb multiple design variables simultaneously using the `additional_perturbations` variable, where we will perturb `additional_perturbations + 1` variables, up to a maximum of `n` variables, where `n` is the total number of design variables.
 
* perturbation_size (float):
    * Description : Value for determining the size of perturbation to each design variable.
    * Default : 0.05
* neighboorhood_search (str):
    * Description : Determine if we apply a fixed perturbation, or a variable perturbation.
    * Default : `fixed`
    * Options : `fixed`, `variable`
    * Note : A variable perturbation applies a pertubation between 0 and `perutbation_size`.
* additional_perturbations (int):
    * Description : Determines if we perturb multiple variables simultaneously.
    * Default : 0
    
### HillClimb

The `HillClimb` agent uses a hill-climbing algorithm to each for optimal solutions.
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
* step_limit (int):
    * Description : Used to determine the total number of steps for the `KaLocalHC` algorithm.
    * Default : 100
* convergence_criteria (float):
    * Description : Used to determine a stopping criteria if the step size drops below this value.
    * Default : 0.001
* hc_type (str):
    * Description : Used to define what type of hill-climb algorithm to use.
    * Default : `simple`
    * Options : `simple`, `steepest-ascent`
    
### GeneticAlgorithm

The `GeneticAlgorithm` agent uses a pseudo-genetic algorithm to search for addition optimal solutions.
We select two designs that are optimal, perform a cross-over of these two designs, and potentially mutate the subsequent designs.
For crossover, there are two available options: `single point `and `linear` crossover.
For mutation, there are two available options: `random` and `non-uniform` mutation.
For `non-uniform `mutation, three additional (`b`, `k`, and `T`) variables can be used to determine the spread of resulting designs.
Distrbution of resulting design variables follows `new design variable + design variable + design variable * rand() ^ (1-k/t)^b`.
For a constant `k`/`T`, smaller values of `b` lead to a larger distribution
For a constant `b`, a smaller `k`/`T` ratio leads to a larger distribution.

* crossover_type (str):
    * Description : Crossover algorithm to use.
    * Default : `single point`
    * Options : `single point`, `linear crossover`
* crossover_rate (float):
    * Description : Fraction of the current pareto front that we want to perform crossover with.
    * Default : 0.8
    * Note : If `offspring_per_generation` is reached before `crossover_rate`, we will terminate early.
* offspring_per_generation (int):
    * Description: Number of designs to generate each time the `KALocalGA` is triggered.
    * Default : 20
    * Note : If `crossover_rate` is reached before `offspring_per_generation`, we will terminate early.
* mutation_type (str):
    * Description : Mutation algorithm to use.
    * Default : `random`
    * Options : `random`, `non-uniform` 
    * Note : For `non-uniform` mutation, we have thee additional variables `b`, `k`, and `T`.
* mutation_rate (float):
    * Description : Fraction of offspring which we will mutate after crossover.
    * Default : 0.1
    
### PyMooAlgorithm

The `PyMooAlgorithm` agent allows for the use of `pymoo` optimization algorithms.
Currently, only the `NSGA-II` algorithm is allowed, however new features will be added in the future.
For descriptions on the algorithm, crossover, and mutations available see [pymoo](https://pymoo.org).
We note that we currently require a population set from the blackboard before the `PyMooAlgorithm` agent activates.
Each time the `PyMooAlgorithm` agent evaluates a solutions, this is written to the blackboard.

* pymoo_algorithm_name (str):
    * Description : Name of the `pymoo` algorithm to be used.
    * Default : `nsga2`
* crossover (str):
    * Description : Name of the `pymoo` crossover type to be used.
    * Default : `real_sbx`    
* mutation (str):
    * Description : Name of the `pymoo` mutation type to be used.
    * Default : `real_pm`
* termination_type (str):
    * Description : Termination type for the `pymoo` algorithm.
    * Default : `n_eval`
    * Note : Default is the number of evaluations.
* termination_criteria (int):
    * Description : Termination criteria for the `pymoo` algorithm.
    * Default : 250
    * Note : For `n_eval` this equates to 250 function (design) evaluations.
* pop_size (int):
    * Description : Population size for the `pymoo` algorithm.
    * Default : 25
* n_offspring (int):
    * Description : Number of offspring for the `pymoo` algorithm.
    * Default : 10