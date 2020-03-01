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
    assert ka_b.get_attr('writer_addr') == None
    assert ka_b.get_attr('writer_alias') == None
    assert ka_b.get_attr('execute_addr') == None
    assert ka_b.get_attr('execute_alias') == None
    assert ka_b.get_attr('trigger_response_addr') == None
    assert ka_b.get_attr('trigger_response_alias') == 'trigger_response_ka_base'
    assert ka_b.get_attr('trigger_publish_addr') == None
    assert ka_b.get_attr('trigger_publish_alias') == None
    assert ka_b.get_attr('trigger_val') == 0

    ns.shutdown()
    time.sleep(0.2)
    
def test_ka_reactor_physics_init():
    ns = run_nameserver()
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    assert ka_rp.get_attr('entry') == None
    assert ka_rp.get_attr('bb') == None
    assert ka_rp.get_attr('writer_addr') == None
    assert ka_rp.get_attr('writer_alias') == None
    assert ka_rp.get_attr('execute_addr') == None
    assert ka_rp.get_attr('execute_alias') == None
    assert ka_rp.get_attr('trigger_response_addr') == None
    assert ka_rp.get_attr('trigger_response_alias') == 'trigger_response_ka_rp'
    assert ka_rp.get_attr('trigger_publish_addr') == None
    assert ka_rp.get_attr('trigger_publish_alias') == None
    
    assert ka_rp.get_attr('trigger_val') == 1   
    assert ka_rp.get_attr('core_name') == None
    assert ka_rp.get_attr('xs_set') == None
    assert ka_rp.get_attr('rx_parameters') == None
    assert ka_rp.get_attr('surrogate_models') == None
    ns.shutdown()
    time.sleep(0.2)

def test_ka_bb_lvl_2_init():
    ns = run_nameserver()
    ka_bb_lvl2 = run_agent(name='ka_bb_lvl2', base=ka.KaBbLvl2)
    assert ka_bb_lvl2.get_attr('entry') == None
    assert ka_bb_lvl2.get_attr('bb') == None
    assert ka_bb_lvl2.get_attr('writer_addr') == None
    assert ka_bb_lvl2.get_attr('writer_alias') == None
    assert ka_bb_lvl2.get_attr('trigger_val') == 0
    assert ka_bb_lvl2.get_attr('execute_addr') == None
    assert ka_bb_lvl2.get_attr('execute_alias') == None
    assert ka_bb_lvl2.get_attr('trigger_response_addr') == None
    assert ka_bb_lvl2.get_attr('trigger_response_alias') == 'trigger_response_ka_bb_lvl2'
    assert ka_bb_lvl2.get_attr('trigger_publish_addr') == None
    assert ka_bb_lvl2.get_attr('trigger_publish_alias') == None
    assert ka_bb_lvl2.get_attr('trigger_val') == 0
    ns.shutdown()
    time.sleep(0.2)
    
    
def test_add_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_bb_lvl2 = run_agent(name='ka_bb_lvl2', base=ka.KaBbLvl2)
    ka_b.add_blackboard(bb)
    ka_rp.add_blackboard(bb)
    ka_bb_lvl2.add_blackboard(bb)
    
    ka_b_bb = ka_b.get_attr('bb')
    ka_b_rp = ka_rp.get_attr('bb')
    ka_b_bb_lvl2 = ka_bb_lvl2.get_attr('bb')
    assert ka_b.get_attr('bb') == bb
    assert ka_b_bb.get_attr('trained_models') == None
    assert ka_rp.get_attr('bb') == bb
    assert ka_b_rp.get_attr('trained_models') == None
    assert ka_bb_lvl2.get_attr('bb') == bb
    assert ka_b_bb_lvl2.get_attr('trained_models') == None
    bb.set_attr(trained_models=10)
    assert ka_b_bb.get_attr('trained_models') == 10
    assert ka_b_rp.get_attr('trained_models') == 10
    assert ka_b_bb_lvl2.get_attr('trained_models') == 10

    assert bb.get_attr('agent_addrs') == {'ka_rp': {}, 'ka_base': {}, 'ka_bb_lvl2': {}}
    ns.shutdown()
    time.sleep(0.2)

def test_connect_writer():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()
    ka_rp.connect_writer()
    assert ka_b.get_attr('writer_alias') == 'write_ka_base'
    assert ka_rp.get_attr('writer_alias') == 'write_ka_rp'
    assert bb.get_attr('agent_addrs')['ka_base']['writer'] == (ka_b.get_attr('writer_alias'), ka_b.get_attr('writer_addr'))
    assert bb.get_attr('agent_addrs')['ka_rp']['writer'] == (ka_rp.get_attr('writer_alias'), ka_rp.get_attr('writer_addr'))
    ns.shutdown()
    time.sleep(0.2)

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
    time.sleep(0.2)
    
def test_connect_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_rp.connect_trigger()
    assert ka_rp.get_attr('trigger_publish_alias') == 'trigger'
    assert ka_b.get_attr('trigger_publish_alias') == 'trigger'
    assert bb.get_attr('agent_addrs')['ka_rp']['trigger_response'] == (ka_rp.get_attr('trigger_response_alias'), ka_rp.get_attr('trigger_response_addr'))
    assert bb.get_attr('agent_addrs')['ka_base']['trigger_response'] == (ka_b.get_attr('trigger_response_alias'), ka_b.get_attr('trigger_response_addr'))
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_lvl2 = run_agent(name='ka_lvl2', base=ka.KaBbLvl2)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    ka_lvl2.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_rp.connect_trigger()
    ka_lvl2.connect_trigger()
    bb.set_attr(trigger_events={1: {}, 2: {}, 10: {}})
    
    bb.publish_trigger()
    time.sleep(0.2)
    assert bb.get_attr('trigger_events') == {1: {'ka_base': 0, 'ka_rp': 1, 'ka_lvl2': 0}, 2: {}, 10: {}}
    bb.set_attr(trigger_event_num=1)
    bb.publish_trigger()
    time.sleep(0.2)
    assert bb.get_attr('trigger_events') == {1: {'ka_base': 0, 'ka_rp': 1, 'ka_lvl2': 0}, 
                                             2: {'ka_base': 0, 'ka_rp': 1, 'ka_lvl2': 0},
                                             10: {}}
    
    bb.set_attr(trigger_event_num=9)
    bb.publish_trigger()
    time.sleep(0.2)
    assert bb.get_attr('trigger_events') == {1: {'ka_base': 0, 'ka_rp': 1, 'ka_lvl2': 0}, 
                                             2: {'ka_base': 0, 'ka_rp': 1, 'ka_lvl2': 0},
                                             10: {'ka_base': 0, 'ka_rp': 1, 'ka_lvl2': 2}}   
    ns.shutdown()
    time.sleep(0.2)    

def test_connect_execute():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_b.add_blackboard(bb)
    try:
        ka_b.connect_execute()
    except NotImplementedError:
        pass
    ka_rp.connect_execute()
    assert ka_rp.get_attr('execute_alias') == 'execute_ka_rp'
    assert bb.get_attr('agent_addrs')['ka_rp']['execute'] == (ka_rp.get_attr('execute_alias'), ka_rp.get_attr('execute_addr'))
    ns.shutdown()
    time.sleep(0.2)

def test_execute_bb_lvl2():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_lvl2 = run_agent(name='ka_lvl2', base=ka.KaBbLvl2)
    ka_lvl2.add_blackboard(bb)
    ka_lvl2.connect_execute()
    
    bb.set_attr(ka_to_execute=('ka_lvl2', 1.0))
    
    bb.send_execute()
    
    assert bb.get_attr('lvl_2') == {}

    ns.shutdown()
    time.sleep(0.2)