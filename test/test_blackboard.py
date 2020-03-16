import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import numpy as np
import blackboard
import knowledge_agent as ka
import time
import os
import h5py
    
def test_blackboard_init_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_agents() == []
    assert bb.get_trained_models() == None
    assert bb.get_attr('agent_addrs') == {}
    for lvl_val, x in zip([{},{},{},{},None],['level 1', 'level 2', 'level 3', 'level 4', 'level 5']):
        assert bb.get_abstract_lvl(x) == lvl_val
    assert bb.get_attr('ka_to_execute') == (None, 0) 
    assert bb.get_attr('trigger_event_num') == 0
    assert bb.get_attr('trigger_events') == {}
    assert bb.get_attr('pub_trigger_alias') == 'trigger'
        
    assert os.path.isfile('blackboard_archive.h5') == True
    bb_archive = h5py.File('blackboard_archive.h5', 'r+')
    
    levels = ['level 1', 'level 2', 'level 3', 'level 4']
    for lvl, bb in zip(levels, bb_archive.keys()):
        assert lvl == bb
    os.remove('blackboard_archive.h5')

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
    bb.add_abstract_lvl(3, {'entry 3': dict})

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

def test_write_to_h5_2():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    os.remove('blackboard_archive.h5')
    
    raw_data = {'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}
    bb.add_abstract_lvl(1, {'entry 1': tuple, 'entry 2': bool})
    bb.add_abstract_lvl(2, {'entry 1': int, 'entry 2': float})
    bb.add_abstract_lvl(3, {'entry 1': dict, 'entry 2': str, 'entry 3': list})
    bb.update_abstract_lvl(1, 'core_2', {'entry 1': (1,1,0), 'entry 2': True})
    bb.update_abstract_lvl(2, 'core_2', {'entry 1': 1, 'entry 2': 1.2})
    bb.update_abstract_lvl(3, 'core_2', {'entry 1': raw_data, 'entry 2': 'test', 'entry 3': [1,2,3]})
    time.sleep(0.5)
    bb.write_to_h5_2()
    
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
    
    raw_data = {'design_1':{'exp_a': 0, 'exp_b': 0, 'exp_c': 0, 'k-eff': 1.0}}
    data = pd.DataFrame.from_dict(raw_data, orient='index')
    #Test writing to the H5 file once
    bb.add_abstract_lvl_1('design_1', (0,0,1), True, True)
    bb.add_abstract_lvl_2('design_1', (0,0,1), False)
    bb.add_abstract_lvl_3('design_1', data, 'xs_set_1')
    bb.write_to_h5()
    
    bb_archive = h5py.File('blackboard_archive.h5', 'r+')

    levels = ['level 1', 'level 2', 'level 3', 'level 4']
    for lvl, bb_lvl in zip(levels, bb_archive.keys()):
        assert lvl == bb_lvl
    lvl1 = bb_archive['level 1']
    lvl2 = bb_archive['level 2']
    lvl3 = bb_archive['level 3']

    assert lvl1['design_1']['exp_num'][0] == 0
    assert lvl1['design_1']['exp_num'][1] == 0
    assert lvl1['design_1']['exp_num'][2] == 1
    assert lvl1['design_1']['validated'][0] == True
    assert lvl1['design_1']['pareto'][0] == True

    assert lvl2['design_1']['exp_num'][0] == 0
    assert lvl2['design_1']['exp_num'][1] == 0
    assert lvl2['design_1']['exp_num'][2] == 1
    assert lvl2['design_1']['valid_core'][0] == False

    for k,v in raw_data['design_1'].items():
        lvl3['design_1']['reactor_parameters'][k][0] == v
    assert lvl3['design_1']['xs_set'][0] == b'xs_set_1'
 
    bb_archive.close()

    #Test writing to the H5 file after it has already been written to
    raw_data = {'design_2':{'exp_a': 1, 'exp_b': 1, 'exp_c': 2, 'k-eff': 1.03}}
    data = pd.DataFrame.from_dict(raw_data, orient='index')    
    bb.add_abstract_lvl_1('design_2', (1,1,2), False, True)
    bb.add_abstract_lvl_2('design_2', (1,1,2), False)
    bb.add_abstract_lvl_3('design_2', data, 'xs_set_2')
    bb.write_to_h5()
    
    bb_archive = h5py.File('blackboard_archive.h5', 'r+')
    
    levels = ['level 1', 'level 2', 'level 3', 'level 4']
    for lvl, bb_lvl in zip(levels, bb_archive.keys()):
        assert lvl == bb_lvl
    lvl1 = bb_archive['level 1']
    lvl2 = bb_archive['level 2']
    lvl3 = bb_archive['level 3']

    assert lvl1['design_2']['exp_num'][0] == 1
    assert lvl1['design_2']['exp_num'][1] == 1
    assert lvl1['design_2']['exp_num'][2] == 2
    assert lvl1['design_2']['validated'][0] == False
    assert lvl1['design_2']['pareto'][0] == True

    assert lvl2['design_2']['exp_num'][0] == 1
    assert lvl2['design_2']['exp_num'][1] == 1
    assert lvl2['design_2']['exp_num'][2] == 2
    assert lvl2['design_2']['valid_core'][0] == False

    for k,v in raw_data['design_2'].items():
        lvl3['design_2']['reactor_parameters'][k][0] == v
    assert lvl3['design_2']['xs_set'][0] == b'xs_set_2'
    
    bb_archive.close()
    os.remove('blackboard_archive.h5')
    
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

def test_controller():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp2 = run_agent(name='ka_rp1', base=ka.KaReactorPhysics)
    bb.set_attr(trigger_events={0: {}})
    
    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    ka_rp.connect_trigger()
    ka_rp.connect_execute()
    ka_rp2.add_blackboard(bb)
    ka_rp2.connect_trigger()
    ka_rp2.set_attr(trigger_val=2)
    
    bb.publish_trigger()
    time.sleep(0.25)
    
    bb.controller()
    assert bb.get_attr('trigger_events') == {0: {}, 1: {'ka_rp': 1, 'ka_rp1': 2}}
    assert bb.get_attr('ka_to_execute') == ('ka_rp1', 2)
    os.remove('blackboard_archive.h5')

    ns.shutdown()
    time.sleep(0.1)