# Blackboard Agent

The BA contains two primary functions; storing the blackboard and communicating with the KAs.
Three abstract levels are present for a typical multi-objective optimization (MOO); *Data Level*, *Viable Design Level*, and *Pareto Front Level*.
*Data Level* consists of specific core design information including all design variables and objective functions.
*Viable Design Level* is an intermediate abstract level which contains core names that fulfill all constraints placed on the objectives.
*Pareto Front Level* consists of the Pareto front and contains optimal reactor designs.
*Data Level* and *Viable Design Level* are further divided into two panels: *new* and *old*.
Knowledge agents (KAs) typically write information to the *new* panel, where the information is processed and moved to the *old* panel by the KA-BR agents This prevents KA-S agents from repeating searchings for the same information.
*Pareto Front Level* does not contain a panel system, as KAs are constantly refining the entries in this level.
In memory, the blackboard is a series of nested dictionaries, which allow KAs to rapidly search these for information of value.
The BA periodically writes the blackboard to an archive in the form of an H5 file.
The archived blackboard allows for ease of analyzing the PF upon completion, restarting the problem, or storing the PF.
We note that most of these variables are able to be set through the [controller](controller.md).

## Attributes

* sm_type (str)
  * Options : interpolate, lr, pr, gpr, ann, rf, custom_plug_in_name
  * Default : interpolate
  * Note : Allows the user to utilize a surrogate model that has been created previously using the `train_surrogate_model` method. The user can create their own custom plug in to a physics solver using the 'custom_plug_in_name'.
  
* design_variables (dict of dicts)
    * Continuous Variable Format: ```{design_variable_name : {'ll': float, 'ul': float, 'variable type': float}}```
        * design_variable_name (str):
          * Description : Name of the design variable.
        * ll (float):
          * Description : Lower limit for the design variable.
        * ul (float):
          * Description : Upper limit for the design variable.
        * 'variable type' (float object):
          * Description : Python `float` object to denote the variable type
    * Discrete Variable Format : ```{design_variable_name: {'options': list of variable_type, 'default': variable_type, 'variable type': [str,int,float]}}```
        * design_variable_name (str):
          * Description : Name of the design variable.  
        * options (list of `variavble type`):
          * Description : List of available discrete options, must contain `defaul` value.
        * default (`variable type`):
          * Description : Default value for discrete variable.
        * 'variable type' (object):
          * Description : Python `float`, `int`, or `str` object to denote the variable type.
    * Example:
        * ```design_variables = {'x0': {'ll':0., 'ul':1., 'variable type': float}, 'x2': {'ll':0., 'ul':7., 'variable type': float}, 'x3' : {'options': ['a', 'b', 'c', 'd', 'e'], 'default': 'e', 'variable type': str}}```

* objectives (dict of dicts):
  * ```{objective_name : {'ll': float, 'ul': float, 'goal': str, variable type': type}}```
    * objective_name (str):
        * Description : Name of the objective function.
        * ll (float):
            * Description : Lower limit for the objective function.
        * ul (float):
            * Description : Upper limit for the objective function.
        * goal (str):
            * Description : Type of optimization to achieve, currently allows minimization (`lt`), maximization (`gt`), and equal to (`et`) a target value.
            * Options : `lt`, `gt`, `et`
        * 'variable type' (object):
            * Description : Python type to denote the variable type.   
            * Options :`float`, `int`, or `list`
        * target (float) : 
            * Description: Value we want to optimize to in `et` optimization goal
            * Note : This parameters is only required for `et` optimization goal.
        * goal_type (str):
            * Description : Value to select for optimizing with a `variable_type` list, currently we can select the maximum value (`max`), minimum value (`min`), average value (`avg`), maximum absolute value (`abs max)`, or minimum absolute value (`abs min`) in a list.
            * Options : `min`, `max`, `avg`, `abs max', `abs min`
            * Note : This parameter is only required if `variable_type` is `list`.
        * length (int):
            * Description : Length of the list.
            * Note : This parameter is only required if `variable_type` is `list`.
    * Example:
        * ```objectives = {'f0': {'ll':0., 'ul':1., 'goal':'lt', 'variable type': float}, 'f1': {'ll':0.,   'ul':1., 'goal':'gt', 'variable type': float}, 'f2': {'ll':0., 'ul':1.,  'goal':'et', 'target': 0.5, 'variable type': float}, 'f3': {'ll':0, 'ul':10, 'goal':'lt', 'variable type': list, 'goal type':'max', 'length': 6}}```

* constraints (dict):
    * ```{constraint_name : {'ll': float, 'ul': float, 'variable type': type}}```
        * Description : Name of the constraint.
        * ll (float):
            * Description : Lower limit for the constraint.
        * ul (float):
            * Description : Upper limit for the constraint
        * 'variable type' (object):
            * Description : Python type to denote the variable type.   
            * Options :`float`, `int`, or `list`              
        * goal_type (str):
            * Description : Value to select for optimizing with a `variable_type` list, currently we can select the maximum value (`max`), minimum value (`min`), average value (`avg`), maximum absolute value (`abs max)`, or minimum absolute value (`abs min`) in a list.
            * Options : `min`, `max`, `avg`, `abs max', `abs min`
            * Note : This parameter is only required if `variable_type` is `list`.
        * length (int):
            * Description : Length of the list.
            * Note : This parameter is only required if `variable_type` is `list`.                        
    * Example:
        * ```constraints = {'c0': {'ll':0., 'ul':150., 'variable type': float}, 'c1': {'ll':0, 'ul':2000, 'variable type': int}, 'c2': {'ll':1.0, 'ul':2.0, 'variable type': float}, 'c3': {'ll':0., 'ul':10., 'variable type': list, 'goal type':'max', 'length': 6}}```
                         
* convergence_model (dict):
  * ```{'type': str, 'convergence rate': val, 'interval': int, 'pf size': int, 'skipped tvs': int, 'total tvs': int, dci_dvi : dict}```
    * type (str):
      * Description : The model used to evaluate the congergence of the problem
      * Options : 'hvi', 'dci hvi', 'total tvs'
      * Note: 'hvi' utilizes the hypervolume indicator to determine the convergence rate.
      * Note: 'dci hvi' utilizes the diversity comparison indicator in conjunction with the hypervolume indicator to determine the convergence rate.
    * convergence rate (float):
      * Description: The differnce between the average HVI for the past `interval` and the previous `interval` value, typically a value between 10E-5 and 10E-6 is adequate.
    * pf size (int):
      * Description: Desired size of the Pareto front, used by the KA-BR agent who examines the `Pareto Level`
    * skipped tvs (int):
        * Description : Number of trigger values to skip before we start comparing the convergence. Typically a value of around 200 is adequate.
    * total_tvs (int):
        * Description : Total number of trigger values to consider if the convergance criteria ha snot been met.
    * dci_dvi (dict):
        * Description : More description to be added later.