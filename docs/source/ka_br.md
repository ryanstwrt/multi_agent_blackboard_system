# Knowledge Agents - Blackboard Reader (KA-BR)

KA-BR agents move designs through the abstract levels to help develop the Pareto front.
There are three agents required for use in an optimiation problem: *Data Reader*, *Promoter*, and *PF Maintainer*.
We note that the three abstract levels are denoted as `data`, `viable design`, and `pareto front`, however, in practice we assign integer values to theses levels as 3, 2, and 1, respectively.
The KA-BR *inter_bb* agent is only used in multi-tiered optimization problems.

## Data Reader

The `data reader` agent examines design on the design level and moves desings which fulfill all objectives and constraints on the problem to the viable design level.
No attributes are available for the KA-BR Data Reader.

## Promoter


The `promoter` agent examines designs on the viable design level with each design on the Pareto front level.
If the design is found to be optimal (i.e. the design is not dominated by any other design), the design is moved to the pareto front level.
No attributes are available for the KA-BR Promoter.

## PF Maintainer

The `PF maintainer` continually refines the PF and removes dominated solutions, and can be used to prune the pareto front level using a variety of methods.
The following attributes are available for the KA-BR PF Maintainer

* pareto_sorter (str):
    * Description : Determines how the Pareto front is maintained. Currently four options are available.
    * Default : `non-dominated`
    * Options: `non-dominated`, `hvi`, `dci`, `dci-hvi`
* total_of_size (int):
    * Description : Determines the maximum allowable number of designs on the PF.
    * Default : 100
    * Note : This option is only available if `pareto_sorter` is not set to `non-dominated`.
    
## Inter BB

The `inter_bb` allows the user to move results from one blackboard to another.

* bb_lvl_write (int):
    * Description : The blackbaord level to write to for the second blackbaord.
    * Default : 3
* bb_lvl_read (int):
    * Description : The blackbaord level to read from.
    * Default : 1
