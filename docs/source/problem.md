# Problem

To set up a blackboard optimization problem, we define a `problem` class.
This allows the user to determine the design variables, objectives, and constraints.
Along with this, the user must define a method for which we use the design variables to evaluate a design and determine the objectives and constraints.

## Design Variables

Design variables are how the variables in an optimization problem that the designer has direct control over.
Currently the MABS, design variables can take four forms: `continuous`, `discrete`, or `permutation`.
Currently, the permutation design variable cannot be mixed with other design variable types.
This ability is currently a work in progress.
To set each design variable type use the template shown below:

Continuous: {'ll': val, 'ul': val, 'variable type': [float, int]}
Discrete: {'options': [list of options], 'variable type': [float, int, str]}
Permutation: {'permutation': [list if items to permutate], 'variable type': [float, int, str]}
    
## Objectives
    
Objectives are how the designer determines what an acceptable or optimal solution looks like.
Currently the MABS accepts four types of objective types: `minimize`, `maximize`, `target`.
    
## Constraints


## Evaluate