import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import blackboard
import knowledge_agent as ka
import time
    
def test_blackboard_init_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_agents() == []
    assert bb.get_trained_models() == None
    assert bb.get_attr('agent_addrs') == {}
    for lvl_val, x in zip([{},{},{},{},None],['level 1', 'level 2', 'level 3', 'level 4', 'level 5']):
        assert bb.get_abstract_lvl(x) == lvl_val
        
    assert bb.get_attr('trigger_event_num') == 0
    assert bb.get_attr('trigger_events') == {}
    assert bb.get_attr('trigger_alias') == 'trigger'
    assert bb.get_attr('trigger_addr') 
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_abstract_lvl_1():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.add_abstract_lvl_1('design_1', (1,1,1), validated=True, pareto=True)
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (1,1,1), 'validated': True, 'pareto': True}}
    ns.shutdown()
    time.sleep(0.1)

def test_update_abstract_lvl_1():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_1('design_1', (0,0,1))
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': False, 'pareto': False}}
    bb.update_abstract_lvl_1('design_1', {'validated': True, 'pareto': True})
    assert bb.get_abstract_lvl('level 1') == {'design_1': {'exp_num': (0,0,1), 'validated': True, 'pareto': True}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_abstract_lvl_2():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.add_abstract_lvl_2('design_1', (1,1,1), True)
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (1,1,1), 'valid_core': True}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_update_abstract_lvl_2():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (0,0,1), 'valid_core': False}}
    bb.update_abstract_lvl_2('design_1', {'valid_core': True})
    assert bb.get_abstract_lvl('level 2') == {'design_1': {'exp_num': (0,0,1), 'valid_core': True}}
    ns.shutdown()
    time.sleep(0.1)

def test_add_abstract_lvl_3():
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

def test_add_abstract_lvl_3_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}    
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    ka_rp.set_attr(core_name='design_1')
    ka_rp.set_attr(rx_parameters=data)
    ka_rp.write_to_bb()
    assert bb.get_abstract_lvl('level 3')['design_1']['xs_set'] == None 
    for k,v in raw_data['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
    ns.shutdown()
    time.sleep(0.1)

def test_add_abstract_lvl_3_agent_overwrite():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}    
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    ka_rp.set_attr(core_name='design_1')
    ka_rp.set_attr(rx_parameters=data)
    ka_rp.write_to_bb()
    for k,v in raw_data['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
        
    raw_data = {'design_1':{'exp_a': 1, 'exp_b': 1, 'exp_c': 1, 'k-eff': 1.2}}    
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    ka_rp.set_attr(core_name='design_1')
    ka_rp.set_attr(rx_parameters=data)
    ka_rp.write_to_bb()
    for k,v in raw_data['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
        
    ns.shutdown()
    time.sleep(0.1)

def test_add_abstract_lvl_3_agent_write_twice():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    
    raw_data1 = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}    
    data = pd.DataFrame.from_dict(raw_data1, orient='index')
    ka_rp.set_attr(core_name='design_1')
    ka_rp.set_attr(rx_parameters=data)
    ka_rp.write_to_bb()
    for k,v in raw_data1['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
        
    raw_data2 = {'design_2':{'exp_a': 1, 'exp_b': 1, 'exp_c': 1, 'k-eff': 1.2}}    
    data = pd.DataFrame.from_dict(raw_data2, orient='index')
    ka_rp.set_attr(core_name='design_2')
    ka_rp.set_attr(rx_parameters=data)
    ka_rp.write_to_bb()
    for k,v in raw_data1['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
    for k,v in raw_data2['design_2'].items():
        assert bb.get_abstract_lvl('level 3')['design_2']['reactor_parameters'][k][0] == v
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_abstract_lvl_3_two_agents_write():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp2 = run_agent(name='ka_rp1', base=ka.KaReactorPhysics)

    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    ka_rp2.add_blackboard(bb)
    ka_rp2.connect_writer()
    
    raw_data1 = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}    
    data = pd.DataFrame.from_dict(raw_data1, orient='index')
    ka_rp.set_attr(core_name='design_1')
    ka_rp.set_attr(rx_parameters=data)
    raw_data2 = {'design_2':{'exp_a': 1, 'exp_b': 1, 'exp_c': 1, 'k-eff': 1.2}}    
    data = pd.DataFrame.from_dict(raw_data2, orient='index')
    ka_rp2.set_attr(core_name='design_2')
    ka_rp2.set_attr(rx_parameters=data)
    
    ka_rp.write_to_bb()
    ka_rp2.write_to_bb()
    for k,v in raw_data1['design_1'].items():
        assert bb.get_abstract_lvl('level 3')['design_1']['reactor_parameters'][k][0] == v
    for k,v in raw_data2['design_2'].items():
        assert bb.get_abstract_lvl('level 3')['design_2']['reactor_parameters'][k][0] == v
    ns.shutdown()
    time.sleep(0.1)

def test_update_abstract_lvl_3():
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


def test_connect_writer():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(agent_addrs={'test':{}})
    bb.connect_writer('test')
    assert bb.get_attr('agent_addrs')['test']['writer'][0] == 'write_test'
    ns.shutdown()
    time.sleep(0.1)

def test_connect_writer_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp2 = run_agent(name='ka_rp1', base=ka.KaReactorPhysics)
    bb.set_attr(agent_addrs={'ka_rp':{}, 'ka_rp1': {}})
    
    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    ka_rp2.add_blackboard(bb)
    ka_rp2.connect_writer()    
    
    assert bb.get_attr('agent_addrs')['ka_rp']['writer'][0] == 'write_ka_rp'
    assert bb.get_attr('agent_addrs')['ka_rp1']['writer'][0] == 'write_ka_rp1'
    
    ns.shutdown()
    time.sleep(0.1)