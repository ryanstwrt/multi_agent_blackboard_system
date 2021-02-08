import src.utils.utilities as utils

def test_scale_float_value():
    assert utils.scale_float_value(5, 0, 10) == 0.5
    assert round(utils.scale_float_value(53, 34, 96), 5) == 0.30645
    
def test_scale_list_value():
    assert utils.scale_list_value([0.0,1.0,2.0,3.0,4.0,5.0], 0.0, 5.0) == [0,0.2,0.4,0.6,0.8,1.0]

def test_scale_value():
    rx =  {'ll':0,   'ul':200, 'goal':'lt', 'variable type': float}
    k =   {'ll':0.0, 'ul':5.0,  'target': 2.5, 'goal':'et', 'variable type': list}
    assert utils.scale_value(200.0, rx) == 1.0
    assert utils.scale_value(0.0, rx) == 0.0
    assert utils.scale_value(100.0, rx) == 0.5
    assert utils.scale_value([0.0,1.0,2.0,3.0,4.0,5.0], k) == [0,0.2,0.4,0.6,0.8,1.0] 
    assert utils.scale_value([[0.0,1.0,2.0,3.0,4.0,5.0], [0.0,1.0,2.0,3.0,4.0,5.0]], k) == [[0,0.2,0.4,0.6,0.8,1.0],[0,0.2,0.4,0.6,0.8,1.0]]

def test_convert_to_minimize():
    rx =  {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float}
    bu =  {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}
    k =   {'ll':1.0, 'ul':2.0,  'target': 1.5, 'goal':'et', 'variable type': float}
    powers = {'ll': 0.0, 'ul': 10.0, 'target': 2.5, 'goal': 'et', 'goal type': 'max', 'variable type': list} 
    bad = {'ll':0,   'ul':15000, 'goal':'tt', 'variable type': float}
    assert utils.convert_objective_to_minimize(bu, 200) == -200
    assert utils.convert_objective_to_minimize(bu, 0.0, scale=True) == 1.0
    assert utils.convert_objective_to_minimize(rx, 200) == 200
    assert utils.convert_objective_to_minimize(bad, 200) == 200
    assert utils.convert_objective_to_minimize(k, 1.25) == 0.25
    assert utils.convert_objective_to_minimize(k, 1.75) == 0.25
    assert utils.convert_objective_to_minimize(k, 0.25, scale=True) == 0.5
    assert utils.convert_objective_to_minimize(powers, [1.0,2.0,3.0,4.0,5.0]) == 2.5
    assert utils.convert_objective_to_minimize(powers, [0.1,0.2,0.3,0.4,0.5], scale=True) == 0.5

def test_get_objective_value():
    assert utils.get_objective_value(9.0) == 9.0
    assert utils.get_objective_value([0.0,1.0,2.0,3.0,4.0,5.0], 'max') == 5.0
    assert utils.get_objective_value([0.0,1.0,2.0,3.0,4.0,5.0], 'min') == 0.0
    assert utils.get_objective_value([0.0,1.0,2.0,3.0,4.0,5.0], 'avg') == 2.5
    assert utils.get_objective_value([[0.0,1.0,2.0,3.0,4.0,5.0], [0.0,1.0,2.0,3.0,4.0,5.0]], 'min') == 0.0
    
def test_pareto_front():
    _lvl_data={'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'power avg':[2.5,5.0,7.5], 'power max':[2.5,5.0,7.5], 'power min':[2.5,5.0,7.5]}},
                               'core_[70.0, 60.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0, 'power avg':[2.5,5.0,7.5], 'power max':[2.5,5.0,7.5], 'power min':[2.5,5.0,7.5]}},
                               'core_[75.0, 55.0, 0.30]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0, 'power avg':[2.5,5.0,7.5], 'power max':[2.5,5.0,7.5], 'power min':[2.5,5.0,7.5]}}}
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'power avg':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'avg'},
            'power max':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'max'},
            'power min':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'min'}}
    pf = ['core_[65.0, 65.0, 0.42]', 'core_[70.0, 60.0, 0.50]', 'core_[75.0, 55.0, 0.30]']
    scaled_pf = utils.scale_pareto_front(pf, objs, _lvl_data)
    assert scaled_pf == [[0.75,0.25,0.5,0.75,0.25], [0.5,0.5,0.5,0.75,0.25], [0.25,0.75,0.5,0.75,0.25]]
    