# Multi-Agent Blackboard System (MABS)

The MABS architecture is used for performing multi-objective optimization for experimental placement in a prototypical test reactor.
Individual agents run high-fidelity simulations to determine reactor parameters, and write this information to the blackboard.
The blackboard is used to store information and partial solutions to determine a maximum number of experimental assemblies that can be placed in a core.
There are four abstraction levels to the blackboard, which stores information gleaned from high-fidelity solutions.
The first level of abstraction contains solutions on the Pareto Front and the number of experiments.
The second level contains basic information from the high-fidelity solutions such as the number of experiments and if the solution produces a valid core.
The third level holds the raw data obtained from high-fidelity solutions in a Pandas Dataframe for ease and searchability.
The fourth level hlds the cross-section sets that are used for the high-fidelity solutions.
A H5 database will also hold the third and fourth levels information to prevent any loss of data should a failure in the MABS system be encountered.