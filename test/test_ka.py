import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import knowledge_agent as ka
import time
import os

def test_ka_init_agent():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    assert ka_b.get_attr('entry') == None
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('rep_addr') == None
    assert ka_b.get_attr('rep_alias') == None
    ns.shutdown()
    time.sleep(0.1)
    
def test_ka_reactor_physics_init():
    ns = run_nameserver()
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    assert ka_rp.get_attr('entry') == None
    assert ka_rp.get_attr('bb') == None
    assert ka_rp.get_attr('rep_addr') == None
    assert ka_rp.get_attr('rep_alias') == None
    
    assert ka_rp.get_attr('trigger_val') == 1   
    assert ka_rp.get_attr('core_name') == None
    assert ka_rp.get_attr('xs_set') == None
    assert ka_rp.get_attr('rx_parameters') == None
    assert ka_rp.get_attr('surrogate_models') == None
    ns.shutdown()
    time.sleep(0.1)

def test_add_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_b.add_blackboard(bb)
    ka_rp.add_blackboard(bb)
    
    ka_b_bb = ka_b.get_attr('bb')
    ka_b_rp = ka_rp.get_attr('bb')
    assert ka_b.get_attr('bb') == bb
    assert ka_b_bb.get_attr('trained_models') == None
    assert ka_rp.get_attr('bb') == bb
    assert ka_b_rp.get_attr('trained_models') == None
    bb.set_attr(trained_models=10)
    assert ka_b_bb.get_attr('trained_models') == 10
    assert ka_b_rp.get_attr('trained_models') == 10

    assert bb.get_attr('agent_addrs') == {'ka_rp': {}, 'ka_base': {}}
    ns.shutdown()
    time.sleep(0.1)

def test_connect_writer():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()
    ka_rp.connect_writer()
    assert ka_b.get_attr('rep_alias') == 'write_ka_base'
    assert ka_rp.get_attr('rep_alias') == 'write_ka_rp'
    assert bb.get_attr('agent_addrs')['ka_base']['writer'] == (ka_b.get_attr('rep_alias'), ka_b.get_attr('rep_addr'))
    assert bb.get_attr('agent_addrs')['ka_rp']['writer'] == (ka_rp.get_attr('rep_alias'), ka_rp.get_attr('rep_addr'))
    ns.shutdown()
    time.sleep(0.1)

def test_write_to_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp2 = run_agent(name='ka_rp2', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp2.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()
    ka_rp.connect_writer()
    ka_rp2.connect_writer()

    assert bb.get_attr('agent_writing') == False
    ka_b.set_attr(core_name='core_1')
    ka_rp.set_attr(core_name='core_2')
    ka_rp2.set_attr(core_name='core_4')
    try:
        ka_b.write_to_bb()
    except NotImplementedError:
        pass
    ka_rp.write_to_bb()
    lvl_3 = bb.get_attr('lvl_3')
    assert bb.get_attr('agent_writing') == False
    assert lvl_3 == {'core_2': {'reactor_parameters': None, 'xs_set': None}}
    ka_rp.set_attr(core_name='core_3')
    ka_rp.write_to_bb()
    ka_rp2.write_to_bb()
    time.sleep(0.5)
    lvl_3 = bb.get_attr('lvl_3')
    assert bb.get_attr('agent_writing') == False
    assert lvl_3 == {'core_2': {'reactor_parameters': None, 'xs_set': None},
                     'core_3': {'reactor_parameters': None, 'xs_set': None},
                     'core_4': {'reactor_parameters': None, 'xs_set': None}}

    ns.shutdown()
    time.sleep(0.1)
    
def test_connect_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger_event()
    ka_rp.connect_trigger_event()
    assert ka_rp.get_attr('trigger_alias') == 'trigger'
    assert ka_b.get_attr('trigger_alias') == 'trigger'
    assert bb.get_attr('agent_addrs')['ka_rp']['trigger'] == ('trigger', ka_rp.get_attr('trigger_addr'))
    assert bb.get_attr('agent_addrs')['ka_base']['trigger'] == ('trigger', ka_rp.get_attr('trigger_addr'))
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger_event()
    ka_rp.connect_trigger_event()
    bb.set_attr(trigger_events={0: {}, 1: {}})
    
    bb.send('trigger', 'event')
    time.sleep(0.5)
    assert bb.get_attr('trigger_events') == {0: {'ka_base': 0, 'ka_rp': 1}, 1: {}}
    bb.set_attr(trigger_event_num=1)
    bb.send('trigger', 'event')
    time.sleep(0.5)
    assert bb.get_attr('trigger_events') == {0: {'ka_base': 0, 'ka_rp': 1}, 
                                             1: {'ka_base': 0, 'ka_rp': 1}}

    ns.shutdown()
    time.sleep(0.1)    