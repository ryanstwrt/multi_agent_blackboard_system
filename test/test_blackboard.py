import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
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
    
def test_add_abstrct_lvl_1():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.add_abstract_lvl_1('design_1', (1,1,1), validated=True, pareto=True)
    assert bb.lvl_1 == {'design_1': {'exp_num': (1,1,1), 'validated': True, 'pareto': True}}
    
def test_update_abstrct_lvl_1():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.update_abstract_lvl_1('design_1', {'validated': True, 'pareto': True})
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': True, 'pareto': True}}

def test_add_abstrct_lvl_2():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.lvl_2 == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.add_abstract_lvl_2('design_1', (1,1,1), True)
    assert bb.lvl_2 == {'design_1': {'exp_num': (1,1,1), 'valid_core': True}}
    
def test_update_abstrct_lvl_2():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.lvl_2 == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.update_abstract_lvl_2('design_1', {'valid_core': True})
    assert bb.lvl_2 == {'design_1': {'exp_num': (0,0,1), 'valid_core': True}}