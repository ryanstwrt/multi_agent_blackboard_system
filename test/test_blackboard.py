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
    
def test_blackboard_init_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_agents() == []
    assert bb.get_trained_models() == None
    for lvl_val, x in zip([{},{},{},{},None],['level 1', 'level 2', 'level 3', 'level 4', 'level 5']):
        assert bb.get_abstract_lvl(x) == lvl_val
    ns.shutdown()
    time.sleep(0.001)
    
def test_add_abstrct_lvl_1():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.add_abstract_lvl_1('design_1', (1,1,1), validated=True, pareto=True)
    assert bb.lvl_1 == {'design_1': {'exp_num': (1,1,1), 'validated': True, 'pareto': True}}
    
def test_add_abstrct_lvl_1_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.add_abstract_lvl_1('design_1', (1,1,1), validated=True, pareto=True)
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (1,1,1), 'validated': True, 'pareto': True}}
    ns.shutdown()
    time.sleep(0.001)
    
def test_update_abstrct_lvl_1():
    bb = blackboard.Blackboard()
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.update_abstract_lvl_1('design_1', {'validated': True, 'pareto': True})
    assert bb.lvl_1 == {'design_1': {'exp_num': (0,0,1), 'validated': True, 'pareto': True}}
    
def test_update_abstrct_lvl_1_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.update_abstract_lvl_1('design_1', {'validated': True, 'pareto': True})
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': True, 'pareto': True}}
    ns.shutdown()
    time.sleep(0.001)