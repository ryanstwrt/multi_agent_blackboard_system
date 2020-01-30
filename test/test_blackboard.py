import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import blackboard
import time

def test_blackboard_init():
    bb = blackboard.Blackboard()
    assert bb.agents == []
    assert bb.trained_models == None
    assert bb.lvl_1 == {}
    assert bb.lvl_2 == {}
    assert bb.lvl_3 == {}
    assert bb.lvl_4 == {}
    
def test_add_abstract_lvl_1():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.add_abstract_lvl_1('design_1', (1,1,1), validated=True, pareto=True)
    assert bb.lvl_1 == {'design_1': {'exp_num': (1,1,1), 'validated': True, 'pareto': True}}
    
def test_update_abstract_lvl_1():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.update_abstract_lvl_1('design_1', {'validated': True, 'pareto': True})
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': True, 'pareto': True}}

def test_add_abstract_lvl_2():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.lvl_2 == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.add_abstract_lvl_2('design_1', (1,1,1), True)
    assert bb.lvl_2 == {'design_1': {'exp_num': (1,1,1), 'valid_core': True}}
    
def test_update_abstract_lvl_2():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.lvl_2 == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.update_abstract_lvl_2('design_1', {'valid_core': True})
    assert bb.lvl_2 == {'design_1': {'exp_num': (0,0,1), 'valid_core': True}}

def test_add_abstract_lvl_3():
    bb = blackboard.Blackboard()
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    bb.add_abstract_lvl_3('design_1', data, 'xs_set_1')
    assert bb.lvl_3['design_1']['xs_set'] == 'xs_set_1' 
    for k,v in raw_data['design_1'].items():
        assert bb.lvl_3['design_1']['reactor_parameters'][k][0] == v

def test_update_abstract_lvl_3():
    bb = blackboard.Blackboard()
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    bb.add_abstract_lvl_3('design_1', data, 'xs_set_1')
    assert bb.lvl_3['design_1']['xs_set'] == 'xs_set_1' 
    for k,v in raw_data['design_1'].items():
        assert bb.lvl_3['design_1']['reactor_parameters'][k][0] == v
    bb.update_abstract_lvl_3('design_1', {'xs_set': 'xs_set_2'})
    assert bb.lvl_3['design_1']['xs_set'] == 'xs_set_2' 
    for k,v in raw_data['design_1'].items():
        assert bb.lvl_3['design_1']['reactor_parameters'][k][0] == v
