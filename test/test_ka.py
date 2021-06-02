import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.bb.blackboard as blackboard
import src.ka.base as ka
import time
import os

def test_ka_init_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('bb_lvl') == 0
    assert ka_b.get_attr('_entry') == None
    assert ka_b.get_attr('_entry_name') == None
    assert ka_b.get_attr('_writer_addr') == None
    assert ka_b.get_attr('_writer_alias') == None
    assert ka_b.get_attr('_executor_addr') == None
    assert ka_b.get_attr('_executor_alias') == None
    assert ka_b.get_attr('_trigger_response_addr') == None
    assert ka_b.get_attr('_trigger_response_alias') == 'trigger_response_ka_base'
    assert ka_b.get_attr('_trigger_publish_addr') == None
    assert ka_b.get_attr('_trigger_publish_alias') == None
    assert ka_b.get_attr('_trigger_val') == 0
    assert ka_b.get_attr('_shutdown_addr') == None
    assert ka_b.get_attr('_shutdown_alias') == None
    ns.shutdown()
    time.sleep(0.05)
    
def test_add_blackboard():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    
    ka_b_bb = ka_b.get_attr('bb')

    assert ka_b.get_attr('bb') == bb
    assert bb.get_attr('agent_addrs') == {'ka_base': {}}
    ns.shutdown()
    time.sleep(0.05)

def test_connect_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_executor()

    assert ka_b.get_attr('_executor_alias') == 'executor_ka_base'
    assert bb.get_attr('agent_addrs')['ka_base']['executor'] == (ka_b.get_attr('_executor_alias'), ka_b.get_attr('_executor_addr'))
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_complete():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_complete()

    assert ka_b.get_attr('_complete_alias') == 'complete_ka_base'
    assert bb.get_attr('agent_addrs')['ka_base']['complete'] == (ka_b.get_attr('_complete_alias'), ka_b.get_attr('_complete_addr'))
    
    ns.shutdown()
    time.sleep(0.05)

def test_connect_trigger_event():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    
    assert ka_b.get_attr('_trigger_publish_alias') == 'trigger'
    assert bb.get_attr('agent_addrs')['ka_base']['trigger_response'] == (ka_b.get_attr('_trigger_response_alias'), ka_b.get_attr('_trigger_response_addr'))
    assert ka_b.get_attr('_trigger_publish_alias') == 'trigger'
    assert ka_b.get_attr('_trigger_publish_addr') == bb.get_attr('_pub_trigger_addr')
    
    ns.shutdown()
    time.sleep(0.05)

def test_connect_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_shutdown()
    assert ka_b.get_attr('_shutdown_alias') == 'shutdown_ka_base'
    assert bb.get_attr('agent_addrs')['ka_base']['shutdown'] == (ka_b.get_attr('_shutdown_alias'), ka_b.get_attr('_shutdown_addr'))
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_writer():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()
    assert ka_b.get_attr('_writer_alias') == 'writer_ka_base'
    assert bb.get_attr('agent_addrs')['ka_base']['writer'] == (ka_b.get_attr('_writer_alias'), ka_b.get_attr('_writer_addr'))
    ns.shutdown()
    time.sleep(0.05)
    
def test_fail_to_connect():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.connect_writer()
    ka_b.connect_executor()
    ka_b.connect_shutdown()
    ka_b.connect_trigger()
    ka_b.connect_complete()
    
    assert ka_b.get_attr('_executor_alias') != 'executor_ka_base'
    assert ka_b.get_attr('_trigger_publish_alias') != 'trigger'
    assert ka_b.get_attr('_trigger_publish_alias') != 'trigger'
    assert ka_b.get_attr('_shutdown_alias') != 'shutdown_ka_base'
    assert ka_b.get_attr('_writer_alias') != 'writer_ka_base'
    ns.shutdown()
    time.sleep(0.05)
        
def test_move_curent_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])

    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_1' : {'valid' : True}}, 'old' : {}}
    ka_base.move_entry(2, 'core_1', {'valid': True}, 'old', 'new')
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old' : {'core_1' : {'valid' : True}}}
    
    ns.shutdown()
    time.sleep(0.05)
    
    
def test_write_to_blackboard():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.set_attr(bb_lvl=1)
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()

    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': list, 'entry 3': str})
    assert bb.get_attr('_agent_writing') == False
    
    ka_b.set_attr(bb_level=1)
    ka_b.write_to_bb(ka_b.get_attr('bb_lvl'), 'core_1', {'entry 1': (0,1,0), 'entry 2': [0,1,0], 'entry 3': 'test'})
    
    assert bb.get_attr('_agent_writing') == False
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': (0,1,0), 'entry 2': [0,1,0], 'entry 3': 'test'}}}

    ns.shutdown()
    time.sleep(0.05)
    
def test_trigger_event():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
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
    time.sleep(0.05)
    assert bb.get_attr('_kaar') == {1: {'ka_base': 0, 'ka_base1': 0, 'ka_base2': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    ka_b1.set_attr(_trigger_val=1)
    bb.publish_trigger()
    bb.controller()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_base': 0, 'ka_base1': 0, 'ka_base2': 0},
                                    2: {'ka_base': 0, 'ka_base1': 1, 'ka_base2': 0}}
    assert bb.get_attr('_ka_to_execute') == ('ka_base1', 1)
    
    ns.shutdown()
    time.sleep(0.05)

def test_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_shutdown()
    assert ns.agents() == ['blackboard', 'ka_base']
    bb.send('shutdown_ka_base', 'message')
    time.sleep(0.05)
    assert ns.agents() ==['blackboard']

    ns.shutdown()
    time.sleep(0.05)          
    
def test_complete():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_complete()
    assert bb.get_attr('_new_entry') == False
    ka_b.action_complete()
    time.sleep(0.05)
    assert bb.get_attr('_new_entry') == True
    ns.shutdown()
    time.sleep(0.05)  