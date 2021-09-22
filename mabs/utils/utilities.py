def convert_objective_to_minimize(obj_dict, obj_val, scale=False):
    """
    Converts maximization and equal to goals to a minimization problem
    """
    goal = obj_dict['goal']
    if obj_dict['variable type'] == list:
        obj_val = get_objective_value(obj_val, goal_type=obj_dict['goal type'])
    
    if goal == 'gt':
        return (1 - obj_val) if scale else -obj_val
    elif goal =='lt':
        return obj_val
    elif goal =='et':
        if scale:
            target = scale_float_value(obj_dict['target'], obj_dict['ll'], obj_dict['ul'])
            return 2 * abs(target - obj_val)
        else:
            return abs(obj_dict['target'] - obj_val)

    else:
        print('Warning: goal for objective with objective dictionary {} given unregistered goal {}. \n Converted to lt (minimization) problem.')
        return obj_val

def convert_pf_to_list(pf, objectives, lvl_data):
    """
    Converte PF to list format.
    """
    # TODO If scale_objective returns a None, we need to figure out how to deal with it.
    # Perhaps cancel the current iteration and tell the BB we are done
    # Should we keep a log of what happened?
    pf_list = []
    for x in pf:
        design_objectives = []
        for obj, obj_dict in objectives.items():
            design_objectives.append(lvl_data[x]['objective functions'][obj])
        pf_list.append(design_objectives)
    return pf_list   
    
def get_float_val(multiplier, ll, ul,  accuracy):
    return round(multiplier * (ul - ll) + ll, accuracy)

def test_limits(val, val_dict):
    if val < val_dict['ll'] or val > val_dict['ul']:
        return True
    return False   

def test_list_limits(val, val_dict):
    for num, v in enumerate(val):
        ll = val_dict['ll'][num] if type(val_dict['ll']) == list else val_dict['ll']
        ul = val_dict['ul'][num] if type(val_dict['ul']) == list else val_dict['ul']
        if v < ll or v > ul:
            return True        
    return False    

def get_objective_value(val, goal_type=None):
    """
    Returns a single value to use as either a fitness function or Pareto indicator if our objective is a list
    If we have a list of list, flatten to a single list.
    """
        
    if type(val) == list:
        try:
            val = [item for sublist in val for item in sublist]
        except TypeError:
            pass
            
    if goal_type == 'max':
        obj_val = max(val)
    elif goal_type == 'min':
        obj_val = min(val)
    elif goal_type == 'avg':
        obj_val = sum(val)/len(val)   
    elif goal_type == 'abs max':
        obj_val = max([abs(x) for x in val])
    elif goal_type == 'abs min':
        obj_val = min([abs(x) for x in val])
    else:
        obj_val = val
        
    return obj_val

def scale_float_value(val, ll, ul):
    """Scale a value based on the lower/upper limits"""
    return (val - ll) / (ul - ll)

def scale_list_value(array, ll, ul):
    """
    Scale all values in a list based on the upper/lower value
    We can scale a 2 dimensional list as well
    """
    scaled_array = []
    for row in array:
        row_array = []
        if type(row) == list:
            row_array = [scale_float_value(col, ll, ul) for col in row]
            scaled_array.append(row_array)
        else:
            scaled_array.append(scale_float_value(row, ll, ul))
    return scaled_array 

def scale_pareto_front(pf, objectives, lvl_data):
    """
    Scale the objective functions for the pareto front and return a scaled pareto front for the hypervolume.
    """
    # TODO If scale_objective returns a None, we need to figure out how to deal with it.
    # Perhaps cancel the current iteration and tell the BB we are done
    # Should we keep a log of what happened?
    scaled_pf = []
    for x in pf:
        design_objectives = []

        for obj, obj_dict in objectives.items():
            scaled_obj_value = scale_value(lvl_data[x]['objective functions'][obj], obj_dict)
            design_objectives.append(round(convert_objective_to_minimize(obj_dict, scaled_obj_value, scale=True), 7))
        scaled_pf.append(design_objectives)
    return scaled_pf

def scale_value(val, val_dict):
    if val_dict['variable type'] == list:
        return scale_list_value(val, val_dict['ll'], val_dict['ul'])
    else:
        return scale_float_value(val, val_dict['ll'], val_dict['ul'])