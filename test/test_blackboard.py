import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import numpy as np
import blackboard
import ka
import time
import os
import h5py
from collections.abc import Iterable
    
def test_blackboard_init_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_attr('agent_addrs') == {}
    assert bb.get_attr('agent_writing') == False
    assert bb.get_attr('new_entry') == False
    assert bb.get_attr('archive_name') == 'blackboard_archive.h5'
    assert bb.get_attr('sleep_limit') == 10

    assert bb.get_attr('abstract_lvls') == {}
    assert bb.get_attr('abstract_lvls_format') == {}
    
    assert bb.get_attr('ka_to_execute') == (None, 0) 
    assert bb.get_attr('trigger_event_num') == 0
    assert bb.get_attr('trigger_events') == {}
    assert bb.get_attr('pub_trigger_alias') == 'trigger'
    
    ns.shutdown()
    time.sleep(0.1)

def test_add_abstract_lvl():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_attr('abstract_lvls') == {}
    assert bb.get_attr('abstract_lvls_format') == {}
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    assert bb.get_attr('abstract_lvls') == {'level 1': {}}
    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'entry 1': str, 'entry 2': bool, 'entry 3': int}}

    ns.shutdown()
    time.sleep(0.1)

def test_connect_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(agent_addrs={'test':{}})
    bb.connect_executor('test')
    assert bb.get_attr('agent_addrs')['test']['executor'][0] == 'executor_test'
    ns.shutdown()
    time.sleep(0.1)
    
def test_connect_executor_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka_b', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_executor()
    assert bb.get_attr('agent_addrs')['ka_b']['executor'][0] == 'executor_ka_b'
    ns.shutdown()
    time.sleep(0.1)
    
def test_connect_trigger_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka_b', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_trigger()
    assert bb.get_attr('agent_addrs')['ka_b']['trigger_response'][0] == 'trigger_response_ka_b'

    ns.shutdown()
    time.sleep(0.1)    
    
def test_connect_writer():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.set_attr(agent_addrs={'test':{}})
    bb.connect_writer('test')
    assert bb.get_attr('agent_addrs')['test']['writer'][0] == 'writer_test'
    ns.shutdown()
    time.sleep(0.1)
    
def test_connect_writer_agent():
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
    time.sleep(0.1)

def test_controller():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_b', base=ka.KaBase)
    ka_b1 = run_agent(name='ka_b1', base=ka.KaBase)
    bb.set_attr(trigger_events={0: {}})   
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b1.add_blackboard(bb)
    ka_b1.connect_trigger()
    ka_b1.set_attr(trigger_val=2)
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('trigger_events') == {0: {}, 1: {'ka_b': 0, 'ka_b1': 2}}
    assert bb.get_attr('ka_to_execute') == ('ka_b1', 2)

    ns.shutdown()
    time.sleep(0.1)
    
def test_send_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_b', base=ka.KaBase)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b.connect_executor()
    bb.set_attr(ka_to_execute=('ka_b',1))
    try:
        bb.send_executor()
    except NotImplementedError:
        pass

    ns.shutdown()
    time.sleep(0.1)    

def test_remove_bb_entry():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})

    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    bb.remove_bb_entry(1, 'core_1')
    assert bb.get_attr('abstract_lvls') == {'level 1': {}}

    ns.shutdown()
    time.sleep(0.1) 
    
def test_remove_bb_entry_agent():
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
    
    ka_base.set_attr(entry_name='core_1')
    ka_base.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    ka_base1.set_attr(entry_name='core_2')
    ka_base1.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    ka_base.write_to_bb()
    ka_base1.write_to_bb()
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                           'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}

    bb.remove_bb_entry(1, 'core_1')
    assert bb.get_attr('abstract_lvls') == {'level 1': {},
                                            'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_update_abstract_lvl():
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
    time.sleep(0.1)

def test_update_abstract_lvl_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)
    ka_base.set_attr(entry_name='core_1')
    ka_base.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})

    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    ka_base.write_to_bb()
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_update_abstract_lvl_overwrite():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})

    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'testing', 'entry 2': True, 'entry 3': 5})
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1' : {'entry 1': 'testing', 'entry 2': True, 'entry 3': 5}}}

    ns.shutdown()
    time.sleep(0.1)   
    
def test_update_abstract_lvl_mult():
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
    time.sleep(0.1)

def test_update_abstract_lvl_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base1 = run_agent(name='ka1', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)
    ka_base.set_attr(entry_name='core_1')
    ka_base.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})

    ka_base1.add_blackboard(bb)
    ka_base1.connect_writer()
    ka_base1.set_attr(bb_lvl=2)
    ka_base1.set_attr(entry_name='core_2')
    ka_base1.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
       
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    ka_base.write_to_bb()
    ka_base1.write_to_bb()
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                            'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}
    ns.shutdown()
    time.sleep(0.1)

def test_rewrite_bb_entry():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_base = run_agent(name='ka', base=ka.KaBase)
    ka_base1 = run_agent(name='ka1', base=ka.KaBase)
    ka_base.add_blackboard(bb)
    ka_base.connect_writer()
    ka_base.set_attr(bb_lvl=1)
    ka_base.set_attr(entry_name='core_1')
    ka_base.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    ka_base1.add_blackboard(bb)
    ka_base1.connect_writer()
    ka_base1.set_attr(bb_lvl=2)
    ka_base1.set_attr(entry_name='core_2')
    ka_base1.set_attr(entry={'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_abstract_lvl(2, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    ka_base.write_to_bb()
    ka_base1.write_to_bb()
    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                           'level 2': {'core_2': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}}}

    ka_base1.set_attr(entry={'entry 1': 'test_new', 'entry 2': True, 'entry 3': 5})
    ka_base1.write_to_bb()    
    assert bb.get_attr('abstract_lvls') == {'level 1': {'core_1': {'entry 1': 'test', 'entry 2': False, 'entry 3': 2}},
                                            'level 2': {'core_2': {'entry 1': 'test_new', 'entry 2': True, 'entry 3': 5}}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_wait_for_ka():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': bool})
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': (1,1,0), 'entry 2': True})
    bb.set_attr(sleep_limit=0.1)
    time.sleep(0.1)
    assert bb.get_attr('new_entry') == False
    bb.wait_for_ka()
    
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
                        assert abs_lvls[k][k1][k2][k3] == v3[0]
                elif type(v2[0]) == np.bytes_:
                    assert abs_lvls[k][k1][k2] == v2[0].decode('UTF-8')
                else:
                    assert np.array(abs_lvls[k][k1][k2]).all() == v2[0].all()
    bb_archive.close()
    os.remove('blackboard_archive.h5')
    ns.shutdown()
    time.sleep(0.1)
    
def test_write_to_h5():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    
    raw_data = {'test_1': (1,1,1), 'test_2': 0.0, 'test_3': 1}
    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': bool})
    bb.add_abstract_lvl(2, {'entry 1': int, 'entry 2': float})
    bb.add_abstract_lvl(3, {'entry 1': {'test_1': tuple, 'test_2': float, 'test_3': int}, 'entry 2': str, 'entry 3': list})
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': (1,1,0), 'entry 2': True})
    bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1, 'entry 2': 1.2})
    bb.update_abstract_lvl(3, 'core_2', {'entry 1': raw_data, 'entry 2': 'test', 'entry 3': [1,2,3]})
    time.sleep(0.1)
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
                        if isinstance(v3[0], Iterable):
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
    time.sleep(0.1)  

def test_load_h5():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    bb1 = run_agent(name='blackboard1', base=blackboard.Blackboard)
    bb1.set_attr(archive_name='blackboard_archive.h5')
    
    raw_data = {'test_1': (1,1,1), 'test_2': 0.0, 'test_3': 1}
    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': bool})
    bb.add_abstract_lvl(2, {'entry 1': int, 'entry 2': float})
    bb.add_abstract_lvl(3, {'entry 1': {'test_1': tuple, 'test_2': float, 'test_3': int}, 'entry 2': str, 'entry 3': list})
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': (1,1,0), 'entry 2': True})
    bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1, 'entry 2': 1.2})
    bb.update_abstract_lvl(3, 'core_2', {'entry 1': raw_data, 'entry 2': 'test', 'entry 3': [1,2,3]})
    time.sleep(0.1)
    bb.write_to_h5()
    time.sleep(1)
    bb1.load_h5()
    
    bb1_bb = bb1.get_attr('abstract_lvls')
    bb_bb = bb.get_attr('abstract_lvls')
    assert bb1_bb == bb_bb
    
    ns.shutdown()   
    os.remove('blackboard_archive.h5')
    
    
    time.sleep(0.1)    