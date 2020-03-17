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
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('bb_lvl') == 0
    assert ka_b.get_attr('entry') == None
    assert ka_b.get_attr('entry') == None
    assert ka_b.get_attr('writer_addr') == None
    assert ka_b.get_attr('writer_alias') == None
    assert ka_b.get_attr('executor_addr') == None
    assert ka_b.get_attr('executor_alias') == None
    assert ka_b.get_attr('trigger_response_addr') == None
    assert ka_b.get_attr('trigger_response_alias') == 'trigger_response_ka_base'
    assert ka_b.get_attr('trigger_publish_addr') == None
    assert ka_b.get_attr('trigger_publish_alias') == None
    assert ka_b.get_attr('trigger_val') == 0
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_add_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    
    ka_b_bb = ka_b.get_attr('bb')

    assert ka_b.get_attr('bb') == bb
    assert bb.get_attr('agent_addrs') == {'ka_base': {}}
    ns.shutdown()
    time.sleep(0.2)

def test_connect_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_executor()

    assert ka_b.get_attr('executor_alias') == 'executor_ka_base'
    assert bb.get_attr('agent_addrs')['ka_base']['executor'] == (ka_b.get_attr('executor_alias'), ka_b.get_attr('executor_addr'))
    
    ns.shutdown()
    time.sleep(0.2)

def test_connect_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    
    assert ka_b.get_attr('trigger_publish_alias') == 'trigger'
    assert bb.get_attr('agent_addrs')['ka_base']['trigger_response'] == (ka_b.get_attr('trigger_response_alias'), ka_b.get_attr('trigger_response_addr'))
    assert ka_b.get_attr('trigger_publish_alias') == 'trigger'
    assert ka_b.get_attr('trigger_publish_addr') == bb.get_attr('pub_trigger_addr')
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_connect_writer():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()
    assert ka_b.get_attr('writer_alias') == 'writer_ka_base'
    assert bb.get_attr('agent_addrs')['ka_base']['writer'] == (ka_b.get_attr('writer_alias'), ka_b.get_attr('writer_addr'))
    ns.shutdown()
    time.sleep(0.2)

def test_write_to_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()

    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': list, 'entry 3': str})
    assert bb.get_attr('agent_writing') == False
    
    ka_b.set_attr(bb_level=1)
    ka_b.set_attr(entry_name='core_1')
    ka_b.set_attr(entry={'entry 1': (0,1,0), 'entry 2': [0,1,0], 'entry 3': 'test'})
    ka_b.write_to_bb()
    
    assert bb.get_attr('agent_writing') == False
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': (0,1,0), 'entry 2': [0,1,0], 'entry 3': 'test'}}}

    ns.shutdown()
    time.sleep(0.2)
    
def test_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b1 = run_agent(name='ka_base1', base=ka.KaBase)
    ka_b2 = run_agent(name='ka_base2', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b1.add_blackboard(bb)
    ka_b2.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b1.connect_trigger()
    ka_b2.connect_trigger()
    
    bb.publish_trigger()
    bb.controller()
    time.sleep(0.2)
    assert bb.get_attr('trigger_events') == {1: {'ka_base': 0, 'ka_base1': 0, 'ka_base2': 0}}
    assert bb.get_attr('ka_to_execute') == (None, 0)
    ka_b1.set_attr(trigger_val=1)
    bb.publish_trigger()
    bb.controller()
    time.sleep(0.2)
    assert bb.get_attr('trigger_events') == {1: {'ka_base': 0, 'ka_base1': 0, 'ka_base2': 0}, 
                                             2: {'ka_base': 0, 'ka_base1': 1, 'ka_base2': 0}}
    assert bb.get_attr('ka_to_execute') == ('ka_base1', 1)
    
    ns.shutdown()
    time.sleep(0.2)