import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import blackboard
import time
    
def test_blackboard_init_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_agents() == []
    assert bb.get_trained_models() == None
    for lvl_val, x in zip([{},{},{},{},None],['level 1', 'level 2', 'level 3', 'level 4', 'level 5']):
        assert bb.get_abstract_lvl(x) == lvl_val
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_abstract_lvl_1_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.add_abstract_lvl_1('design_1', (1,1,1), validated=True, pareto=True)
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (1,1,1), 'validated': True, 'pareto': True}}
    ns.shutdown()
    time.sleep(0.1)

def test_update_abstract_lvl_1_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.update_abstract_lvl_1('design_1', {'validated': True, 'pareto': True})
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': True, 'pareto': True}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_abstract_lvl_2_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.add_abstract_lvl_2('design_1', (1,1,1), True)
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (1,1,1), 'valid_core': True}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_update_abstract_lvl_2_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.update_abstract_lvl_2('design_1', {'valid_core': True})
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (0,0,1), 'valid_core': True}}
    ns.shutdown()
    time.sleep(0.1)

def test_add_abstract_lvl_3_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    bb.add_abstract_lvl_3('design_1', data, 'xs_set_1')
    assert bb.get_abstract_lvl('level 3')['design_1']['xs_set'] == 'xs_set_1' 
    for k,v in raw_data['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
    ns.shutdown()
    time.sleep(0.1)

    
def test_update_abstract_lvl_3_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    bb.add_abstract_lvl_3('design_1', data, 'xs_set_1')
    assert bb.get_abstract_lvl('level 3')['design_1']['xs_set'] == 'xs_set_1' 
    for k,v in raw_data['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
    bb.update_abstract_lvl_3('design_1', {'xs_set': 'xs_set_2'})
    assert bb.get_abstract_lvl('level 3')['design_1']['xs_set'] == 'xs_set_2' 
    for k,v in raw_data['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
    ns.shutdown()
    time.sleep(0.1)

def test_connect_REP_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.connect_REP_agent('test')
    
    assert bb.get_attr('agent_addrs')['test']['alias'] == 'write_0'
    
    ns.shutdown()
    time.sleep(0.1)


def test_write_to_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.connect_REP_agent('test')
    assert bb.get_attr('agent_writing') == False
    bb.write_to_blackboard('test')
    assert bb.get_attr('agent_writing') == True
    
    ns.shutdown()
    time.sleep(0.1)