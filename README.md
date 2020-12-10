[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/ryanstwrt/multi_agent_blackboard_system.svg?branch=master)](https://travis-ci.org/ryanstwrt/multi_agent_blackboard_system)
[![Coverage Status](https://coveralls.io/repos/github/ryanstwrt/multi_agent_blackboard_system/badge.svg?branch=master)](https://coveralls.io/github/ryanstwrt/multi_agent_blackboard_system?branch=master)

# Multi-Agent Blackboard System

The multi-agent blackboard system (MABS) is a general use blackboard framework, which employs the use of multiple agents.
Multiple agents are allowed to exist and operate concurrently using osBrain [1].
The MABS has a skeletal framework that introduces the basic components for the blackboard and knowledge agents.
Users can leverage these components and build a blackboard system which is able to accommodate their needs.

## Documentation

Documentation can be found [Here](https://ryanstwrt.github.io/MABS/).


## Multi-Agent Blackboard for Continuous and Discrete Optimization

MABS has a been extended to allow for both continuous and discrete optimization.
Provided is a brief example for setting up a benchmark optimization problem.
We first need to set up the problem by importing the controller, ka_rp, and ka_br classes.

```
import src.controller as controller
import src.ka_rp as karp
import src.ka_br as kabr

model = 'sf1'
objs = {'f1': {'ll':0, 'ul':4, 'goal':'lt', 'variable type': float},
        'f2': {'ll':0, 'ul':4, 'goal':'lt', 'variable type': float}}
dvs =  {'x1':  {'ll':-10, 'ul':10, 'variable type': float}}
const = {}

kas = {'ka_rp_explore': karp.KaGlobal, 
       'ka_rp_ns': karp.KaLocal,
       'ka_br_lvl3': kabr.KaBr_lvl3,
       'ka_br_lvl2': kabr.KaBr_lvl2,
       'ka_br_lvl1': kabr.KaBr_lvl1}

bb_controller = controller.BenchmarkController(ka=kas, 
                                      objectives=objs, 
                                      design_variables=dvs,
                                      constraints=const,
                                      benchmark=model)
```
For this benchmark, we are examining the Schaffer Function 1 benchmark problem (`sf1`).
The two objective functions are labeled `f1` and `f2`, where we describe the lower limits (`ll`), upper limits (`ul`), the type of optimization - minimiation (`goal`), and the variable type (`variable type`).
There is one design variable `x1`, where we describe the lower limits (`ll`), upper limits (`ul`), and the variable type (`variable type`).
There are no additional constraints.
In this problem we utilize five knowledge agents: three agents for assessing the blackboard (KA-BR agents) and two agents to seach the design space (KA-RP agents).
We run the problem by invoking the `run_multi_agent_bb()` or `run_single_agent_bb`

```
bb_controller.run_multi_agent_bb()
```
Upon completion, an H5 file will be present in the directory which contains all of the data from the run in three abstract levels.
The first level contains the names for the Pareto front.
The second level contains designs that meet the objectives.
The third level contains the data for each design, including the design variables, objective functions, and any constraints.

[1] osBrain v0.6.5, (2019), GitHub repository, https://github.com/opensistemas-hub/osbrain.