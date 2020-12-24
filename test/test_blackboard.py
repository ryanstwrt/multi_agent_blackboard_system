import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import numpy as np
import src.blackboard as blackboard
import src.ka as ka
import src.ka_rp as karp
import time
import os
import h5py
from collections.abc import Iterable
    
def test_blackboard_init_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_attr('agent_addrs') == {}
    assert bb.get_attr('_agent_writing') == False
    assert bb.get_attr('_new_entry') == False
    assert bb.get_attr('archive_name') == 'blackboard_archive.h5'
    assert bb.get_attr('_sleep_limit') == 10

    assert bb.get_attr('abstract_lvls') == {}
    assert bb.get_attr('abstract_lvls_format') == {}
    
    assert bb.get_attr('_ka_to_execute') == (None, 0) 
    assert bb.get_attr('_trigger_event') == 0
    assert bb.get_attr('_kaar') == {}
    assert bb.get_attr('_pub_trigger_alias') == 'trigger'
    
    ns.shutdown()
    time.sleep(0.05)

def test_add_abstract_lvl():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_attr('abstract_lvls') == {}
    assert bb.get_attr('abstract_lvls_format') == {}
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    assert bb.get_attr('abstract_lvls') == {'level 1': {}}
    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'entry 1': str, 'entry 2': bool, 'entry 3': int}}

    ns.shutdown()
    time.sleep(0.05)

def test_add_panel():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': int})
    assert bb.get_attr('abstract_lvls') == {'level 1': {}}
    bb.add_panel(1, ['panel_a', 'panel_b', 'panel_c'])
    assert bb.get_attr('abstract_lvls') == {'level 1': {'panel_a': {},'panel_b': {},'panel_c': {}}}
    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'panel_a': {'entry 1': str, 'entry 2': int},
                                                               'panel_b': {'entry 1': str, 'entry 2': int},
                                                               'panel_c': {'entry 1': str, 'entry 2': int}}}
    
    bb.update_abstract_lvl(1, 'test_name', {'entry 1': 'foo', 'entry 2': 5})
    assert bb.get_attr('abstract_lvls') == {'level 1': {'panel_a': {},'panel_b': {},'panel_c': {}}}
    bb.update_abstract_lvl(1, 'test_name', {'entry 1': 'foo', 'entry 2': 5}, panel='panel_a')
    assert bb.get_attr('abstract_lvls') == {'level 1': {'panel_a': {'test_name': {'entry 1': 'foo', 'entry 2': 5}},'panel_b': {},'panel_c': {}}}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(agent_addrs={'test':{}})
    bb.connect_executor('test')
    assert bb.get_attr('agent_addrs')['test']['executor'][0] == 'executor_test'
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_executor_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka_b', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_executor()
    assert bb.get_attr('agent_addrs')['ka_b']['executor'][0] == 'executor_ka_b'
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_trigger_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka_b', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_trigger()
    assert bb.get_attr('agent_addrs')['ka_b']['trigger_response'][0] == 'trigger_response_ka_b'

    ns.shutdown()
    time.sleep(0.05)    

def test_connect_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(agent_addrs={'test':{}})
    bb.connect_shutdown('test')
    assert bb.get_attr('agent_addrs')['test']['shutdown'][0] == 'shutdown_test'

    ns.shutdown()
    time.sleep(0.05) 
    
def test_connect_shutdown_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka', base=ka.KaBase)
    ka_b.add_blackboard(bb)    
    ka_b.connect_shutdown()
    assert bb.get_attr('agent_addrs')['ka']['shutdown'][0] == 'shutdown_ka'

    ns.shutdown()
    time.sleep(0.05) 
    
def test_connect_writer():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(agent_addrs={'test':{}})
    bb.connect_writer('test')
    assert bb.get_attr('agent_addrs')['test']['writer'][0] == 'writer_test'
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_writer_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka', base=ka.KaBase)
    ka_b1 = run_agent(name='ka_b1', base=ka.KaBase)
    bb.set_attr(agent_addrs={'ka':{}, 'ka_b1': {}})
    
    ka_b.add_blackboard(bb)
    ka_b.connect_writer()
    ka_b1.add_blackboard(bb)
    ka_b1.connect_writer()    
    assert bb.get_attr('agent_addrs')['ka']['writer'][0] == 'writer_ka'
    assert bb.get_attr('agent_addrs')['ka_b1']['writer'][0] == 'writer_ka_b1'
    
    ns.shutdown()
    time.sleep(0.05)

def test_connect_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.connect_agent(ka.KaBase, 'base')
    
    agents = bb.get_attr('agent_addrs')
    
    assert [x for x in agents.keys()] == ['base']
    assert ns.agents() == ['blackboard', 'base']

    base = ns.proxy('base')
    
    assert bb.get_attr('agent_addrs')['base']['executor'] == (base.get_attr('_executor_alias'), base.get_attr('_executor_addr'))
    assert bb.get_attr('agent_addrs')['base']['trigger_response'] == (base.get_attr('_trigger_response_alias'), base.get_attr('_trigger_response_addr'))
    assert bb.get_attr('agent_addrs')['base']['shutdown'] == (base.get_attr('_shutdown_alias'), base.get_attr('_shutdown_addr'))
    assert bb.get_attr('agent_addrs')['base']['writer'] == (base.get_attr('_writer_alias'), base.get_attr('_writer_addr'))
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_controller():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_b', base=ka.KaBase)
    ka_b1 = run_agent(name='ka_b1', base=ka.KaBase)
    bb.set_attr(_kaar={0: {}})   
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b1.add_blackboard(bb)
    ka_b1.connect_trigger()
    ka_b1.set_attr(_trigger_val=2)
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {0: {}, 1: {'ka_b': 0, 'ka_b1': 2}}
    assert bb.get_attr('_ka_to_execute') == ('ka_b1', 2)

    ns.shutdown()
    time.sleep(0.05)

def test_diagnostics_agent_present():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.diagnostics_agent_present('blank') == False
    ka_b = run_agent(name='ka_b', base=ka.KaBase)
    assert bb.diagnostics_agent_present('ka_b') == True

    ns.shutdown()
    time.sleep(0.05)

def test_diagnostics_replace_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(required_agents=[ka.KaBase])
    bb.connect_agent(ka.KaBase, 'ka_b')
    ka_b = ns.proxy('ka_b')
    
    assert ns.agents() == ['blackboard', 'ka_b']
    bb.diagnostics_replace_agent()
    assert ns.agents() == ['blackboard', 'ka_b']
    bb.send('shutdown_ka_b', 'message')
    time.sleep(0.05)
    assert ns.agents() == ['blackboard']
    bb.diagnostics_replace_agent()
    assert ns.agents() == ['blackboard', 'ka_b']
    bb.set_attr(_ka_to_execute=('ka_b',1))
    bb.send_executor()
    bb.diagnostics_replace_agent()
    assert ns.agents() == ['blackboard', 'ka_b']

    ns.shutdown()
    time.sleep(0.05)  
    
def test_get_blackbaord():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': int})
    bb.add_panel(1, ['panel_a', 'panel_b', 'panel_c'])

    
    bb.update_abstract_lvl(1, 'test_name', {'entry 1': 'foo', 'entry 2': 5})
    bb.update_abstract_lvl(1, 'test_name', {'entry 1': 'foo', 'entry 2': 5}, panel='panel_a')
    assert bb.get_blackboard() == {'level 1': {'panel_a': {'test_name': {'entry 1': 'foo', 'entry 2': 5}},'panel_b': {},'panel_c': {}}}
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_get_kaar():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(_kaar={1: {'ka': 0, 'ka2': 1}})
    
    assert bb.get_kaar() == {1: {'ka': 0, 'ka2': 1}}
    
    ns.shutdown()
    time.sleep(0.05)    
    
def test_get_current_trigger_value():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(_trigger_event=10)
    
    assert bb.get_current_trigger_value() == 10
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_send_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_b', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b.connect_executor()
    bb.set_attr(_ka_to_execute=('ka_b',1))
    try:
        bb.send_executor()
    except NotImplementedError:
        pass

    ns.shutdown()
    time.sleep(0.05)    

def test_remove_bb_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_panel(2, ['new', 'old'])
    
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    bb.update_abstract_lvl(2, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}, panel='new')
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}, 'level 2': {'new' : {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}, 'old': {}}}
        
    bb.remove_bb_entry(1, 'core_1')
    bb.remove_bb_entry(2, 'core_1', panel='new')
    assert bb.get_attr('abstract_lvls') == {'level 1': {}, 'level 2': {'new':{}, 'old':{}}}

    ns.shutdown()
    time.sleep(0.05) 
    
def test_remove_bb_entry_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base1 = run_agent(name='ka1', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)
    ka_base1.add_blackboard(bb)
    ka_base1.connect_writer()
    ka_base1.set_attr(bb_lvl=2)
    
    ka_base.write_to_bb(ka_base.get_attr('bb_lvl'), 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    ka_base1.write_to_bb(ka_base1.get_attr('bb_lvl'), 'core_2', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                           'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}

    bb.remove_bb_entry(1, 'core_1')
    assert bb.get_attr('abstract_lvls') == {'level 1': {},
                                            'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    ns.shutdown()
    time.sleep(0.05)
    
def test_update_abstract_lvl():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})

    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': 'test', 'entry 2': False, 'entry 4': 2})    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}

    bb.update_abstract_lvl(1, 'core_2', {'entry 1': 'test', 'entry 2': False, 'entry 3': False})
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}

    bb.update_abstract_lvl(1, 'core_2', {'entry 1': 'test_2', 'entry 2': True, 'entry 3': 6})
    assert bb.get_attr('abstract_lvls') == {'level 1': 
                                            {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}, 
                                             'core_2':  {'entry 1': 'test_2', 'entry 2': True, 'entry 3': 6}}}
    
    ns.shutdown()
    time.sleep(0.05)

def test_update_abstract_lvl_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)

    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    ka_base.write_to_bb(ka_base.get_attr('bb_lvl'), 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    ns.shutdown()
    time.sleep(0.05)
    
def test_update_abstract_lvl_overwrite():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})

    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'testing', 'entry 2': True, 'entry 3': 5})
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'testing', 'entry 2': True, 'entry 3': 5}}}

    ns.shutdown()
    time.sleep(0.05)   
    
def test_update_abstract_lvl_mult():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': float, 'entry 2': str})
    bb.add_abstract_lvl(3, {'entry 3': {'foo': float, 'spam': float}})

    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': 'test_2', 'entry 2': True, 'entry 3': 6})
    bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1.2, 'entry 2': 'testing'})
    bb.update_abstract_lvl(3, 'core_2', {'entry 3': {'foo': 1.1, 'spam': 3.2}})

    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}, 
                                                        'core_2': {'entry 1': 'test_2', 'entry 2': True, 'entry 3': 6}},
                                            'level 2': {'core_2': {'entry 1': 1.2, 'entry 2': 'testing'}},
                                            'level 3': {'core_2': {'entry 3': {'foo': 1.1, 'spam': 3.2}}}}
    ns.shutdown()
    time.sleep(0.05)

def test_update_abstract_lvl_multi_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base1 = run_agent(name='ka1', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)

    ka_base1.add_blackboard(bb)
    ka_base1.connect_writer()
    ka_base1.set_attr(bb_lvl=2)
       
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    ka_base.write_to_bb(ka_base.get_attr('bb_lvl'), 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    ka_base1.write_to_bb(ka_base1.get_attr('bb_lvl'), 'core_2',{'entry 1': 'test', 'entry 2': False, 'entry 3': 2} )
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                            'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    ns.shutdown()
    time.sleep(0.05)

def test_rewrite_bb_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base1 = run_agent(name='ka1', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)
    
    ka_base1.add_blackboard(bb)
    ka_base1.connect_writer()
    ka_base1.set_attr(bb_lvl=2)
    
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    ka_base.write_to_bb(ka_base.get_attr('bb_lvl'), 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    ka_base1.write_to_bb(ka_base1.get_attr('bb_lvl'), 'core_2', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                           'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}

    ka_base1.write_to_bb(ka_base1.get_attr('bb_lvl'), 'core_2', {'entry 1': 'test_new', 'entry 2': True, 'entry 3': 5})    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                            'level 2': {'core_2': {'entry 1': 'test_new', 'entry 2': True, 'entry 3': 5}}}
    ns.shutdown()
    time.sleep(0.05)
    
def test_write_to_h5():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    
    raw_data = {'test_1': (1,1,1), 'test_2': 0.0, 'test_3': 1}
    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': bool})
    bb.add_abstract_lvl(2, {'entry 1': int, 'entry 2': float})
    bb.add_abstract_lvl(4, {'entry 1': {'test 1': {'nested_test': int}}})
    bb.add_abstract_lvl(3, {'entry 1': {'test_1': tuple, 'test_2': float, 'test_3': int}, 'entry 2': str, 'entry 3': list})
    bb.add_panel(1, ['new','old'])
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': (1,1,0), 'entry 2': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1, 'entry 2': 1.2})
    bb.update_abstract_lvl(3, 'core_2', {'entry 1': raw_data, 'entry 2': 'test', 'entry 3': [1,2,3]})
    bb.update_abstract_lvl(4, 'core_4', {'entry 1': {'test 1': {'nested_test': 3}}})

    
    time.sleep(0.05)
    bb.write_to_h5()
    
    abs_lvls = bb.get_attr('abstract_lvls')
    bb_archive = h5py.File('blackboard_archive.h5', 'r+')
    
    for k,v in bb_archive.items():
        assert k in abs_lvls.keys()
        for k1,v1 in v.items():
            assert k1 in abs_lvls[k].keys()
            for k2,v2 in v1.items():
                assert k2 in abs_lvls[k][k1].keys()
                if type(v2) == h5py.Group:
                    for k3,v3 in v2.items():
                        if isinstance(v3, h5py._hl.group.Group):
                            assert abs_lvls[k][k1][k2][k3]['nested_test'] == v3['nested_test'][0]
                        elif isinstance(v3[0], Iterable):
                            assert list(abs_lvls[k][k1][k2][k3]) == list(v3[0])
                        else:
                            assert abs_lvls[k][k1][k2][k3] == v3[0]
                elif type(v2[0]) == np.bytes_:
                    assert abs_lvls[k][k1][k2] == v2[0].decode('UTF-8')
                else:
                    assert np.array(abs_lvls[k][k1][k2]).all() == v2[0].all()

    bb_archive.close()
    os.remove('blackboard_archive.h5')
    ns.shutdown()    
    time.sleep(0.05) 

def test_load_h5():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb_h5 = run_agent(name='blackboard1', base=blackboard.Blackboard)
    bb_h5_2 = run_agent(name='blackboard2', base=blackboard.Blackboard)
    bb_h5.set_attr(archive_name='blackboard_archive.h5')
    bb_h5_2.set_attr(archive_name='blackboard_archive.h5')

    
    raw_data = {'test_1': (1,1,1), 'test_2': 0.0, 'test_3': 1}
    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': bool})
    bb.add_panel(1, ['new','old'])
    bb.add_abstract_lvl(2, {'entry 1': int, 'entry 2': float})
    bb.add_abstract_lvl(3, {'entry 1': {'test_1': tuple, 'test_2': float, 'test_3': int}, 'entry 2': str, 'entry 3': list})
    bb.add_abstract_lvl(4, {'entry 1': {'test 1': {'nested_test': int}}})
    
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': (1,1,0), 'entry 2': True}, panel = 'new')
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': (1,1,0), 'entry 2': True}, panel = 'old')
    bb.update_abstract_lvl(1, 'core_3', {'entry 1': (1,1,0), 'entry 2': True}, panel = 'old')

    
    bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1, 'entry 2': 1.2})
    bb.update_abstract_lvl(3, 'core_3', {'entry 1': raw_data, 'entry 2': 'test', 'entry 3': [1.1,2.0,3.0]})
    bb.update_abstract_lvl(4, 'core_4', {'entry 1': {'test 1': {'nested_test': 3}}})
    
    time.sleep(0.05)
    bb.write_to_h5()
    time.sleep(3)
    bb_h5.load_h5(panels={1: ['new','old']})
    
    bb_h5_bb = bb_h5.get_attr('abstract_lvls')
    bb_bb = bb.get_attr('abstract_lvls')

    assert bb_h5_bb == bb_bb

    bb.update_abstract_lvl(2, 'core_3', {'entry 1': 1, 'entry 2': 1.2})
    bb.remove_bb_entry(2, 'core_2')
    bb.remove_bb_entry(1, 'core_1', panel='new')
    bb.write_to_h5()
    time.sleep(3)

    
    bb_h5_2.load_h5(panels={1: ['new','old']})
    bb_h5_bb = bb_h5_2.get_attr('abstract_lvls')
    bb_bb = bb.get_attr('abstract_lvls')
    assert bb_h5_bb == bb_bb
    
    ns.shutdown()   
    os.remove('blackboard_archive.h5')
    
    time.sleep(0.05)

def test_h5_group_writer():
    """
    Function cannot current be isolated to test, cannot pickle an H5 file to send to the agent
    """
    pass
#    ns = run_nameserver()
 #   bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    
    #bb.add_abstract_lvl(2, {'entry 1': int, 'entry 2': float})
    #bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1, 'entry 2': 1.2})
    #bb.write_to_h5()
    #time.sleep(1)
    
#    h5 = h5py.File('blackboard_archive.h5', 'w')
 #   h5.create_group('level 1')
  #  h5_group = h5['level 1']
    
#    bb.h5_group_writer(h5_group, 'entry 1', {'a': 1, 'b': 3})  
 #   assert h5['level 1']['entry 1'] == {'a': 1, 'b': 3}

 #   ns.shutdown()   
  #  os.remove('blackboard_archive.h5')
    
   # time.sleep(0.05)

def test_connect_sub_blackboard():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    
    bb.connect_sub_blackboard('sub_bb', blackboard.Blackboard)
    sub_bb = bb.get_attr('_sub_bbs')
    assert [x for x in sub_bb.keys()] == ['sub_bb']
    sub_bb = sub_bb['sub_bb']
    assert sub_bb.get_attr('name') == 'sub_bb'
    assert sub_bb.get_attr('archive_name') == 'sub_bb.h5'
    
    ns.shutdown()       
    time.sleep(0.05)  