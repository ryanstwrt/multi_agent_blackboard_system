# Multi-Agent Blackboard System (MABS)

## Overview

MABS is a framework for generating a blackboard system that can run in parallel by utilizing a multi-agent environment.
This is exemplified by its use as a multi-objective optimization framework. 
It allows the user to define multiple design variables (these can be continuous or discrete), multiple objective functions (these can be continuous or list-like), and multiple constraints (these can be continueous or list-like).
The MABS framework allows the user to perform on optimization problem using a surrogate model, or creating a plug-in for their own unique solver.
For a typical optimization problem, we require give major components: the blackboard agent (BA), search knowledge agent (KA-S), blackboard reader knowledge agent (KA-BR), the contoller agent (CA), and a problem statement. 

## Contents

* [BA](source/blackboard.md)
* [KA-S](source/ka_s.md)
* [KA-BR](source/ka_br.md)
* [CA](source/controller.md)
* [Problem](source/problem.md)